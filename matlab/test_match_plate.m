% [bw1, im1] = load_bw('H:\Experimental Datas\Cosmo\lifespan-20180718\G7\2018-06-06__13-33-57.tiff');
% [bw2, im2] = load_bw('H:\Experimental Datas\Cosmo\lifespan-20180718\G7\2018-06-06__21-33-57.tiff');
% [bw3, im3] = load_bw('H:\Experimental Datas\Cosmo\lifespan-20180718\G7\2018-06-22__01-17-08.tiff');
% 
% % imagesc(bw1); axis equal;
% 
% bw3(1479:1964, 2978:3592) = 1;
% mmt1 = moment2(bw1);
% mmt2 = moment2(bw2);
% mmt3 = moment2(bw3);

thedir = 'H:\Experimental Datas\Cosmo\lifespan-20180718\G7';
files = dir(thedir);
nfiles = 105;
mmts = zeros(nfiles, 2);
files = files(end-nfiles+1:end);

% for i = 1:105
%     bwi = load_bw(fullfile(thedir, files(i).name));
%     mmts(i, :) = moment2(bwi);
% end

% subplot(211), plot(1:nfiles, mmts(:,1));
% subplot(212), plot(1:nfiles, mmts(:,2));

% [bw1, im1] = load_bw(fullfile(thedir, files(61).name));
% [bw2, im2] = load_bw(fullfile(thedir, files(62).name));

[bw1, im1] = load_bw(fullfile(thedir, files(85).name));
[bw2, im2] = load_bw(fullfile(thedir, files(86).name));

% mmt1 = moment2(bw1);
% mmt2 = moment2(bw2);

% threshold = 15;
% [mmt1, bw1] = parameter_ellipse(im1, threshold); mmt1 = fliplr(mmt1.Centroid);
% [mmt2, bw2] = parameter_ellipse(im2, threshold); mmt2 = fliplr(mmt2.Centroid);

sliceid = [5138,1401;5287,1546];

% slice1 = im1 - im2;
% slice2 = im1 - image_shift(im2, round(mmt1 - mmt2));
% slice3 = (255 - im1) * 0.15;
% slice1 = slice1(sliceid(1,1):sliceid(2,1), sliceid(1,2):sliceid(2,2));
% slice2 = slice2(sliceid(1,1):sliceid(2,1), sliceid(1,2):sliceid(2,2));
% slice3 = slice3(sliceid(1,1):sliceid(2,1), sliceid(1,2):sliceid(2,2));
% figure;
% subplot(221); imagesc(abs(slice1)); axis equal;
% subplot(222); imagesc(abs(slice2)); axis equal;
% subplot(223); imagesc(merge_image(abs(slice1), abs(slice3), [])); axis equal;
% subplot(224); imagesc(merge_image(abs(slice2), abs(slice3), [])); axis equal;

shifting = fliplr(round(mmt1 - mmt2));
% shifting(1) = 0;
im2shift = image_shift(im2, shifting);
slice1 = 255 - im1;
slice2 = 255 - im2;
slice3 = 255 - im2shift;
% slice1 = slice1(sliceid(1,1):sliceid(2,1), sliceid(1,2):sliceid(2,2));
% slice2 = slice2(sliceid(1,1):sliceid(2,1), sliceid(1,2):sliceid(2,2));
% slice3 = slice3(sliceid(1,1):sliceid(2,1), sliceid(1,2):sliceid(2,2));
figure;
% imagesc(merge_image(slice1, slice2, [])); axis equal;
subplot(121); imagesc(merge_image(slice1, slice2, [])); axis equal;
subplot(122); imagesc(merge_image(slice1, slice3, [])); axis equal;
% imagesc(abs(slice1 - slice3)); axis equal;

function [bw, img] = load_bw(filename)

img = imread(filename);
bw = img > 15;
% bw = medfilt2(bw, [1,1] * 17);
bw = double(bw);

end