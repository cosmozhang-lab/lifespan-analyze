function [im2shift, shifting] = match_plate(im1, im2, varargin)
threshold = 35;
usegpu = 1;
for i = 1:length(varargin)
    if strcmpi(varargin{i}, 'nogpu')
        usegpu = 0;
    end
end
im1mem = im1;
im2mem = im2;
if usegpu
    im1 = gpuArray(im1mem);
    im2 = gpuArray(im2mem);
end
mmt1 = parameter_ellipse(im1, threshold); mmt1 = fliplr(mmt1.Centroid);
mmt2 = parameter_ellipse(im2, threshold); mmt2 = fliplr(mmt2.Centroid);
shifting = fliplr(round(mmt1 - mmt2));
im2shift = image_shift(im2mem, shifting);
