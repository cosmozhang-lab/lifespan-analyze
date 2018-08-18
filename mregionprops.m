function [ out ] = mregionprops( bwlabels, varargin )
% mregionprops: calculate region properties marked by bwlabels
% Input:
%     bwlabels: Region labels. Can be calculated by bwlabels
%     ...: Properties to calculate ('Area', 'Centroid')
% Output:
%     1xN struct where N is the number of regions, with fields:
%         Area, Centroid
%         Fields will only apear if you choose the option

opt_area = 0;
opt_centroid = 0;

thecoors = [];

for i = 1:length(varargin)
    if strcmpi(varargin{i}, 'area')
        opt_area = 1;
    elseif strcmpi(varargin{i}, 'centroid')
        opt_centroid = 1;
    elseif strcmpi(varargin{i}, 'coors')
        i = i+1;
        thecoors = varargin{i};
    end
end

nregions = max(max(bwlabels));
isgpu = isa(bwlabels, 'gpuArray');

bwregion = cast(bwlabels > 0, 'uint32');
if opt_centroid
    bwregion_by_coory = bwregion.* thecoors(1);
    bwregion_by_coorx = bwregion.* thecoors(2);
end

out = struct;
for i = 1:nregions
    theregion = cast(bwlabels == i, 'uint32');
    thearea = [];
    if opt_centroid
        thearea = calc_area(thearea, theregion);
        thecoors = m_make_coors(thecoors, size(theregion), isgpu);
        cx = sum(sum(theregion .* bwregion_by_coorx)) / thearea;
        cy = sum(sum(theregion .* bwregion_by_coory)) / thearea;
        out(i).Centroid = [cy, cx];
    end
    if opt_area
        thearea = calc_area(thearea, theregion);
        out(i).Area = thearea;
    end
end

end

function [area] = calc_area(fmout, theregion)
if isempty(fmout)
    area = sum(sum(theregion));
else
    area = fmout;
end
end

function [coors] = m_make_coors(fmout, regionsize, isgpu)
if isempty(fmout)
    coors = make_coors(regionsize);
    if isgpu
        coors = gpuArray(coors);
    end
else
    coors = fmout;
end
end

