function s = parameter_ellipse(I,threshold)

bw = ~(I < threshold);
% bw = medfilt2(bw, [13 13]);
L = bwlabel(bw);
stats = regionprops(L,'Area');
maxid = find([stats.Area] == max([stats.Area]));
bw = (L == maxid);
imfill(bw, 'holes');
s = regionprops(bw, 'Centroid');
