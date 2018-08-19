function  [out] = death_judgment(bw_manager, fcurent, finterval, tolerance_diedrate)
% ***************************************************************************
% Function: Calculate the deaths of C. elegans in the current frame.(Include having died)
%   Input:
%             bw_manager: ImageManager
%             fcurent: The curent frame
%             finterval: The time interval for judging death. The default is 4.
%             tolerance_diedrate: The criteria for judging death(died), defined as overlapping area ratio. The default is 0.9.
%   Output:
%             num_deaths: The death for curent frame.(Include having died)
%             bwdeaths: <GPU> 2-D binary image defined as the dead C. elegans for curent frame.(Include having died)
% Author: Zhe Zhang
% Date: 2018/8/16
% Edit: Jiazhi Zhang
% Date: 2018/8/18
% ***************************************************************************

tic;

if fcurent < finterval
   error('Error. fcurent must be larger than finterval.')
end

tic;

bw = gpuArray(zeros(bw_manager.size(), 'uint8'));
for i = fcurent-finterval+1:fcurent
    bw = cast(bw_manager.gpu_image(i), 'uint8') + bw;
end
bw = (bw == finterval);
bw = cast(bw, 'uint8');
bbwcurrent = bw_manager.gpu_image(fcurent);
bwcurrent = cast(bbwcurrent, 'uint8');
imoverlap = bwcurrent + bw;
L = bwlabel(bwcurrent);
stats = regionprops(gather(L), 'Area');
num_deaths = 0;
bwdeaths = gpuArray(zeros(size(imoverlap), 'uint8'));
for j = 1:length(stats)
    bbwregion = (L == j);
    uibwregion = cast(bbwregion, 'uint8');
    bwregion = uibwregion .* imoverlap;
    area_ratio = sum(sum(bwregion == 2)) /stats(j).Area ;
    if area_ratio > tolerance_diedrate
        bwdeaths = bwdeaths + uibwregion;
        bwdeaths = min(bwdeaths, 1);
        num_deaths = num_deaths + 1;
    end
end
bwdeaths = cast(bwdeaths,'logical');

out.num_deaths = num_deaths;
out.bw_deaths = bwdeaths;

% tt = toc; tic; fprintf('1. time = %f\n', tt);
