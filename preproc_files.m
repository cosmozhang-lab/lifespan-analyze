load_params;

plate = 'H12';
nfiles = 105;

% mmts = zeros([imagesize, nfiles], 'uint8');
% mmts_bw = zeros([imagesize, nfiles], 'uint8');
% files = get_file_list(plate);
% files = files(end-nfiles+1:end);

% % single frame - registration
% mmts(:, :, 1) = imread(files(1).fullpath);
% imshifts = zeros([nfiles, 2], 'double');
% fprintf('loaded %d / %d\n', 1, nfiles);
% for i = 2:nfiles
%     imi = imread(files(i).fullpath);
%     [im2shift,shifting] = match_plate(mmts(:,:,i-1), imi);
%     imshifts(i,:) = shifting;
%     mmts(:, :, i) = im2shift;
%     fprintf('loaded %d / %d\n', i, nfiles);
% end

% single frame - segmentation of C. elegans
for i = 1:nfiles
    bw = detect_worm_2d(mmts(:, :, i), minsize, maxsize);
    mmts_bw(:, :, i) = bw;
    fprintf('detected %d / %d\n', i, nfiles);
end

% save(sprintf('./data/%s.mat', plate), '-v7.3', 'mmts', 'mmts_bw', 'imshifts', 'plate', 'nfiles');
