function [ outim ] = image_shift( img, varargin )

if length(varargin) < 2 || ~isnumeric(varargin{2})
    shifts = varargin{1};
else
    shifts = [varargin{1}, varargin{2}];
end

shiftx = shifts(1);
shifty = shifts(2);

imh = size(img, 1);
imw = size(img, 2);
imc = size(img, 3);
ashiftx = abs(shiftx);
ashifty = abs(shifty);
outim = zeros(size(img) + abs([shifty, shiftx]) * 2);
top = 1 + ashifty + shifty;
bottom = top + imh - 1;
left = 1 + ashiftx + shiftx;
right = left + imw - 1;
outim(top:bottom, left:right, :) = img;
top = 1 + ashifty;
bottom = top + imh - 1;
left = 1 + ashiftx;
right = left + imw - 1;
outim = outim(top:bottom, left:right, :);
outim = cast(outim, class(img));

end

