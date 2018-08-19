function [out] = death_count(bwdeaths1_ori,bwdeaths2_ori,tolerance_havingdiedrate)
% ***************************************************************************
% Function: Calculate the deaths of C. elegans in the current frame.(Not include having died)
%   Input:
%             bwdeaths1_ori: <GPU> 2-D binary image defined as the dead C. elegans for last frame
%             bwdeaths2_ori: <GPU> 2-D binary image defined as the dead C. elegans for curent frame
%             num_deaths2_ori: The death for curent frame
%             tolerance_havingdiedrate:The criteria for judging death(having died), defined as overlapping area ratio. The default is 0.5.
%   Output:
%             struct with fields:
%                 num_deaths: The death for curent frame.(Not include having died)
%                 bwdeaths: 2-D binary image defined as the dead C. elegans for curent frame.(Not include having died)
% Author: Zhe Zhang
% Date: 2018/8/16
% Edit: Jiazhi Zhang
% Date: 2018/8/18
% ***************************************************************************

L = bwlabel(bwdeaths2_ori);
nworms = max(max(L));
bbwdeaths2_ori = cast(bwdeaths2_ori, 'logical');
stats = regionprops(bbwdeaths2_ori,{...
    'Area',...
    'Centroid'});
imdeaths_overlap = cast(bwdeaths1_ori + bwdeaths2_ori, 'uint8');
bwdeaths2 = gpuArray(zeros(size(imdeaths_overlap), 'uint8'));
num_deaths2 = 0;
bwregion = gpuArray(zeros(size(L), 'uint8'));
for j = 1:length(stats)
    bwregion(:,:) = 0;
    bbwregion = (L == j);
    bwregion(bbwregion) = 1;
    bwregion = bwregion .* imdeaths_overlap;
    area_ratio = sum(sum(bwregion == 2)) / stats(j).Area;
    if area_ratio < tolerance_havingdiedrate
        bwdeaths2(bbwregion) = 1;
        num_deaths2 = num_deaths2 + 1;
    end
end

out.num_deaths = num_deaths2;
out.bw_deaths = bwdeaths2;