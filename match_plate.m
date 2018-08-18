function im2shift = match_plate(filesname1,filesname2,thedir)
im1 = imread(fullfile(thedir, filesname1));
im2 = imread(fullfile(thedir, filesname2));

threshold = 15;
mmt1 = parameter_ellipse(im1, threshold); mmt1 = fliplr(mmt1.Centroid);
mmt2 = parameter_ellipse(im2, threshold); mmt2 = fliplr(mmt2.Centroid);

shifting = fliplr(round(mmt1 - mmt2));
im2shift = image_shift(im2, shifting);