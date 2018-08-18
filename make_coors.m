function [coors] = make_coors(region)
if length(region) == 2
    regionsize = region;
else
    regionsize = [size(region,1), size(region,2)];
end
coors = zeros([regionsize, 2], 'uint32');
coors(:,:,1) = transpose(repmat(0:regionsize(1)-1, [regionsize(2),1]));
coors(:,:,2) = repmat(0:regionsize(2)-1, [regionsize(1),1]);
end