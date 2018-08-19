function BW = detect_worm_2d(I,minsize,maxsize)
% ***************************************************************************
% Function: Identify the location of C. elegans based on area selection.
%   Input: 
%             I: 2-D grayscale image
%             minsize: The manimum area of C. elegans
%             maxsize: The maximum area of C. elegans
%   Output:
%             BW: 2-D binary image 
% Author: Zhe Zhang
% Date: 2018/8/09
% ***************************************************************************

% otsu
level=graythresh(I);     % Threshold segmentation
BW=im2bw(I,level);
% imopen
se = strel('disk',3);
BW = imopen(BW,se);
% area selection
BW = gpuArray(BW);
[L,num] = bwlabel(~BW);
stats = regionprops(L);     % Area filter
BW = ismember(L, find([stats.Area] < maxsize));
BW = bwareaopen(BW,minsize);
% imfill
BW = imfill(BW,'holes');
BW = gather(BW);

end






