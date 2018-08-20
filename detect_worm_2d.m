function BW = detect_worm_2d(I,minsize,maxsize,varargin)
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

usegpu = 1;

for i = 1:length(varargin)
    if strcmpi(varargin{i}, 'nogpu')
        usegpu = 0;
    end
end

% otsu
isgpu = isa(I, 'gpuArray');
if isgpu
    I = gather(I);
end
level=graythresh(I);     % Threshold segmentation
BW = im2bw(I,level);
if usegpu
    BW = gpuArray(BW);
end
% imopen
se = strel('disk',3);
BW = imopen(BW,se);
% area selection
[L,num] = bwlabel(~BW);
stats = regionprops(L, 'Area');     % Area filter
areas = [stats.Area];
BW = ismember(L, find((areas < maxsize) & (areas > minsize)));
% imfill
BW = imfill(BW,'holes');

if ~isgpu
    BW = gather(BW);
end

end






