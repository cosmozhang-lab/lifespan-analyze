%******************************************************************
%
% An example to show how to calculate survival curve
%
%******************************************************************

t1=clock;

% initialize
thedir = 'G:\CONTENT\Experimental_Datas\lifespan-20180718\G7';
nfiles = 105;
minsize = 700; %可以尝试缩小面积范围，减少线虫误判率。如�?00�?500）修改为�?000,3500�?
maxsize = 3500;
finterval = 4;
tolerance_diedrate = 0.9;
tolerance_havingdiedrate = 0.5;

% single frame - registration and segmentation of C. elegans
files = dir(thedir);
files = files(end-nfiles+1:end);
mmts(:, :, 1) = imread(fullfile(thedir, files(1).name));
for i = 2:nfiles
    im2shift = match_plate(files(1).name,files(i).name,thedir);
    mmts(:, :, i) = im2shift;
    bw = detect_worm_2d(im2shift,minsize,maxsize);
    mmts_bw(:, :, i) = bw;
end

% % show segmentation
% i = 100;
% [L,num] = bwlabeln(mmts_bw(:,:,i));
% RGB = label2rgb(L);
% figure;imshow(RGB);
% stats = regionprops(L);
% centroid = cat(1, stats.Centroid);
% x = centroid(:,1);
% y = centroid(:,2);
% figure;imshow(mmts(:,:,i));hold on;plot(x,y,'r*');

% % show registration
% slice1 = 255 - mmts(:, :, 85);
% slice2 = 255 - mmts(:, :, 86);
% figure;imagesc(merge_image(slice1, slice2, [])); axis equal;

% Multiple frames- death judgment of C. elegans
num_deaths = zeros([finterval-1,1]);
% mmts_bwdeaths = [];
fcurent = finterval;
[num_deaths1,bwdeaths1] = death_judgment(mmts_bw,fcurent,tolerance_diedrate,finterval);
% mmts_bwdeaths(:, :, fcurent) = bwdeaths1;
num_deaths = [num_deaths;num_deaths1];

for fcurent2 = finterval+1:nfiles
    fcurent1 = fcurent2 - 1;
    [num_deaths2,bwdeaths2] = cframe_death_count(mmts_bw,fcurent1,fcurent2,finterval,tolerance_diedrate,tolerance_havingdiedrate);
    num_deaths = [num_deaths;num_deaths2];
%     mmts_bwdeaths(:, :, fcurent2) = bwdeaths2;
end

% show survival curve
plot(num_deaths)
saveas(gcf,'result.png')

t2=clock;
etime(t2,t1)

% save('result.mat','num_deaths','mmts_bwdeaths','-v7.3')
% save('-v7.3')





    


