import lifespan.common.mainparams as mp
import numpy as np, cv2, torch
import skimage
from lifespan.common.algos import make_coors, torch_bwcentroid
from .image_manager import StepAnalyze

def drawout_piece(image, centroid, halfsize):
    centroid = np.round(centroid).astype(np.int32)
    halfsize = np.array(halfsize).astype(np.int32)
    pieceout = torch.zeros(tuple(halfsize*2-1), dtype=image.dtype, device=image.device)
    rectcur = np.concatenate((centroid - halfsize + 1, centroid + halfsize))
    rectoff = -np.min((rectcur[0:2], (0,0)), axis=0)
    rectcur[0:2] += rectoff
    piececur = image[rectcur[0]:rectcur[2], rectcur[1]:rectcur[3]]
    pieceout[rectoff[0]:rectoff[0]+piececur.shape[0], rectoff[1]:rectoff[1]+piececur.shape[1]] = piececur
    return pieceout

class DeathDetector:
    def __init__(self, images):
        self.images = images
        # 设共重标记到的死虫数目为N，而总的帧数为T
        # bwdeaths为长度为N的数组，每个元素为一个511*511的torch.cuda.BoolTensor，存储了第i条死虫的各帧二值图的并集，以globalcentroids中存储的质心为图像中心
        self.bwdeaths = []
        # globalids为N*T的数组，每行对应一条死虫在各帧所重标记的原始虫编号（从1开始），而0表示那一帧没能匹配到虫子
        self.globalids = None
        # globalcentroids为N*2的数组，每一行对应一条死虫的质心坐标[y,x]
        self.globalcentroids = None

    def step(self, index):
        if self.images[index].step >= StepAnalyze:
            return True
        if self.images[index].error:
            return False
        if self.images[index].gpuwormbwl is None:
            self.images[index].gpuwormbwl = torch.cuda.ByteTensor(self.images[index].wormbwl)
        if index < mp.finterval-1:
            return False
        self.death_judge(index, mp.finterval, mp.death_overlap_threshold)
        self.death_select(index, mp.finterval, mp.death_overlap_threshold_for_selecting)
        self.images[index].step = StepAnalyze
        return True
    
    # 检测虫子是否处于存活/死亡状态
    def death_judge(self, fcurrent, finterval, overlap_threshold):
        # 首先要保证现在及过去的finterval帧中没有错误发生
        for i in range(fcurrent - finterval + 1, fcurrent + 1):
            if self.images[i].error:
                return
        # 开始检测虫子的存活状态
        bwshapehf = np.array(mp.marksize)
        bwoverlap = torch.zeros(tuple(bwshapehf*2-1), dtype=torch.bool, device="cuda")
        nbwl = min(self.images[fcurrent].wormcentroids.shape[0], 255)
        # 遍历所有的虫子
        for i in range(nbwl):
            # 在当前帧中，对于每条虫子
            # 取出当前虫子的511*511的二值图像（以当前虫子的质心为中心）
            # 并初始化bwoverlap为当前虫子的中心
            labelcur = i + 1
            centroidcur = np.round(self.images[fcurrent].wormcentroids[i,:])
            piececur = drawout_piece(self.images[fcurrent].gpuwormbwl, centroidcur, bwshapehf) == labelcur
            bwoverlap[:,:] = True
            bwoverlap[:,:] &= piececur
            areacur = torch.sum(bwoverlap.type(torch.uint8))
            # 遍历过去的finterval-1帧，做重标记，并计算重叠率
            for j in range(fcurrent - 2, fcurrent - finterval, -1):
                # 在第j帧中，寻找所有与当前虫子质心距离在distthre距离范围内的虫子
                # 从这些虫子中选择与当前虫子重叠面积最大的那一条，作为当前虫子在第j帧中对应的重标记虫
                # 并将bwoverlap与重标记虫的二值图像求交集
                if self.images[fcurrent-1].wormcentroids is None or self.images[fcurrent-1].wormcentroids.shape[0] == 0:
                    bwoverlap[:,:] = False
                    break
                # 计算所有虫子距离当前帧虫子的距离，选择distthre范围内的虫子
                dists = np.sqrt(np.sum((centroidcur - self.images[fcurrent-1].wormcentroids)**2, axis=1))
                ihiss = np.where(dists <= mp.distthre)[0]
                if ihiss.shape[0] == 0:
                    bwoverlap[:,:] = False
                    break
                # 通过循环遍历上面找到的虫子，确定重标记的虫子
                areaomax = 0
                imatch = None
                piecematch = None
                for ihis in list(ihiss):
                    labelhis = ihis + 1
                    centroidhis = np.round(self.images[fcurrent-1].wormcentroids[ihis,:])
                    piecehis = drawout_piece(self.images[j].gpuwormbwl, centroidhis, bwshapehf) == labelhis
                    areao = int(torch.sum(piecehis & piececur))
                    if areaomax < areao:
                        areaomax = areao
                        imatch = ihis
                        piecematch = piecehis
                # if float(areaomax) / float(areacur) < overlap_threshold:
                #     bwoverlap[:,:] = False
                #     break
                if imatch is None:
                    bwoverlap[:,:] = False
                    break
                # 将bwoverlap与这条虫子求交集
                bwoverlap[:,:] &= piecematch
            # 计算bwoverlap占当前虫子面积areacur的比例，即重叠率
            areao = torch.sum(bwoverlap.type(torch.uint8))
            area_ratio = float(areao) / float(areacur)
            self.images[fcurrent].score_deathdetect[i] = area_ratio
            if area_ratio >= overlap_threshold:
                # 重叠率满足阈值条件，记为死亡
                self.images[fcurrent].wormdead[i] = True
    
    # 对死亡虫子进行重标记，即检测当前帧中的死虫是否曾经已经被记为死亡
    def death_select(self, fcurrent, bwdeaths, overlap_threshold):
        bwshapehf = np.array(mp.marksize)
        # 新的实例成员变量，将在所有重标记工作完成后覆盖现有变量
        bwdeaths = []
        globalids = []
        globalcentroids = []
        unmatchedids = list(range(len(self.bwdeaths)))
        # 遍历当前帧中所有的死虫子
        for i in range(min(self.images[fcurrent].wormdead.shape[0], 255)):
            if not self.images[fcurrent].wormdead[i]:
                continue
            # 对于每条死虫，从过去已重标记的死虫中寻找对应的死虫，即距离在distthre范围内的重叠面积最大的虫
            # 首先取出当前虫子的511*511的二值图像（以当前虫子的质心为中心）
            labelcur = i + 1
            centroidcur = np.round(self.images[fcurrent].wormcentroids[i,:])
            piececur = drawout_piece(self.images[fcurrent].gpuwormbwl, centroidcur, bwshapehf) == labelcur
            areacur = int(torch.sum(piececur))
            imatch = None # 准备存储匹配到的过去死虫的重标记序号（即在self.bwdeaths、self.globalids、self.globalcentroids中的下标）
            if self.globalcentroids is not None:
                # 找出过去已重标记死虫中与当前帧当前死虫距离在distthre范围内的死虫
                dists = np.sqrt(np.sum((centroidcur - self.globalcentroids)**2, axis=1))
                ihiss = np.where(dists <= mp.distthre)[0]
                areaomax = 0
                imaxa = None
                piecemaxa = None
                # 遍历找到的所有死虫，寻找与当前帧当前死虫重叠面积最大的那条死虫
                for ihis in list(ihiss):
                    centroidhis = np.round(self.globalcentroids[ihis,:])
                    piecehis = self.bwdeaths[ihis]
                    areao = int(torch.sum(piecehis & piececur))
                    if areaomax < areao:
                        areaomax = areao
                        imaxa = ihis
                        piecemaxa = piecehis
                area_ratio = float(areaomax) / float(areacur)
                self.images[fcurrent].score_deathselect[i] = area_ratio
                if area_ratio > 0 and area_ratio >= overlap_threshold:
                    # 若重叠率满足阈值条件，则成功匹配到重标记，记录下重标记号
                    imatch = imaxa
            if imatch is not None:
                # 若匹配到重标记，那么需要更新重标记到的死虫的质心、二值图像和globalid序列，加入到新的globalcentroids、bwdeaths和globalids中去
                globalidrow = self.globalids[imatch,:].copy()
                nmatchhis = int(np.sum(globalidrow > 0))
                globalidrow[fcurrent] = labelcur
                globalcentroidrow = self.globalcentroids[imatch,:].copy()
                globalcentroidrow = (globalcentroidrow.astype(np.float32) * nmatchhis + centroidcur.astype(np.float32)) / (nmatchhis + 1)
                bwdeathitem = self.bwdeaths[imatch] | piececur
                if imatch in unmatchedids:
                    unmatchedids.remove(imatch)
            else:
                # 否则就创建一条新的重标记虫，初始化其质心、二值图像和globalid序列，加入到新的globalcentroids、bwdeaths和globalids中去
                # 并且将当前帧当前虫标记为当前帧死亡的
                globalidrow = np.zeros((len(self.images),), dtype=np.int32)
                globalidrow[fcurrent] = labelcur
                globalcentroidrow = centroidcur.copy()
                bwdeathitem = piececur.clone()
                self.images[fcurrent].wormdies[i] = True
            # 将更新后的或新创建的质心、二值图像和globalid序列加入到新的globalcentroids、bwdeaths和globalids中去
            bwdeaths.append(bwdeathitem)
            globalids.append(globalidrow)
            globalcentroids.append(globalcentroidrow)
        # 用新的bwdeaths、globalids、globalcentroids覆盖实例中原有的这三个变量
        bwdeaths = [self.bwdeaths[i] for i in unmatchedids] + bwdeaths
        globalids = [self.globalids[i,:] for i in unmatchedids] + globalids
        globalcentroids = [self.globalcentroids[i,:] for i in unmatchedids] + globalcentroids
        if len(bwdeaths) > 0:
            self.bwdeaths = bwdeaths
            self.globalids = np.stack(globalids, axis=0)
            self.globalcentroids = np.stack(globalcentroids, axis=0)
        else:
            self.bwdeaths = []
            self.globalids = None
            self.globalcentroids = None
