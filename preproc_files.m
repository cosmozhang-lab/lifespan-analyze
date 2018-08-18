plate = 'G7';
nfiles = 105;
minsize = 700;
maxsize = 3500;
finterval = 4;
tolerance_diedrate = 0.9;
tolerance_havingdiedrate = 0.5;

% single frame - registration and segmentation of C. elegans
files = get_file_list(plate);
files = files(end-nfiles+1:end);
mmts(:, :, 1) = imread(fullfile(thedir, files(1).name));
for i = 2:nfiles
    im2shift = match_plate(files(1).name,files(i).name,thedir);
    mmts(:, :, i) = im2shift;
    bw = detect_worm_2d(im2shift,minsize,maxsize);
    mmts_bw(:, :, i) = bw;
end