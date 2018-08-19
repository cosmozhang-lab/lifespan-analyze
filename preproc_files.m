load_params;

plate = 'G7';
nfiles = 105;
minsize = 700;
maxsize = 3500;
finterval = 4;
tolerance_diedrate = 0.9;
tolerance_havingdiedrate = 0.5;

% single frame - registration and segmentation of C. elegans
mmts = zeros([imagesize, nfiles], 'uint8');
mmts_bw = zeros([imagesize, nfiles], 'uint8');
files = get_file_list(plate);
files = files(end-nfiles+1:end);
mmts(:, :, 1) = imread(files(1).fullpath);
fprintf('loaded %d / %d\n', 1, nfiles);
for i = 2:nfiles
    imi = imread(files(i).fullpath);
    im2shift = match_plate(mmts(:,:,i-1), imi);
    mmts(:, :, i) = im2shift;
    bw = detect_worm_2d(im2shift,minsize,maxsize);
    mmts_bw(:, :, i) = bw;
    fprintf('loaded %d / %d\n', i, nfiles);
end

save([plate '.mat'], '-v7.3', 'mmts', 'mmts_bw', 'plate', 'nfiles');
