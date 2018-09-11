% manager_options = struct;
% manager_options.extbuffs = struct;
% manager_options.extbuffs.bw = (@(im) detect_worm_2d(im, minsize, maxsize));
% manager = ImageManager(mmts, finterval + 1, 0, manager_options);
% manager.load(1);

bw_manager = ImageManager(mmts_bw, finterval + 1);
bw_manager.load(1);

num_deaths = zeros(1, nfiles);
centroids_after_exclude = cell(1, nfiles);
centroids_before_exclude = cell(1, nfiles);
centroids_origin = cell(1, nfiles);

% Multiple frames- death judgment of C. elegans
ds1 = death_judgment(bw_manager, finterval, finterval, tolerance_diedrate);
bw_manager.next();
num_deaths(finterval) = ds1.num_deaths;
centroids_after_exclude{finterval} = ds1.centroids;
centroids_before_exclude{finterval} = ds1.centroids;
centroids_origin{finterval} = ds1.centroids_ori;
bw_deaths = gpuArray(ds1.bw_deaths);
for fcurent2 = finterval + 1:nfiles
    fcurent1 = fcurent2 - 1;
    ds2 = death_judgment(bw_manager, fcurent2, finterval, tolerance_diedrate);
    ds3 = death_count(bw_deaths, ds2.bw_deaths, tolerance_havingdiedrate);
    bw_deaths = bw_deaths | ds2.bw_deaths;
    bw_manager.next();
    num_deaths(fcurent2) = ds3.num_deaths;
    centroids_after_exclude{fcurent2} = ds3.centroids;
    centroids_before_exclude{fcurent2} = ds2.centroids;
    centroids_origin{fcurent2} = ds2.centroids_ori;
    ds1 = ds2;
    if verbose >= 10
        fprintf('analyzed: %d / %d\n', fcurent2, nfiles);
    end
end

save(sprintf('./out/result-%s.mat', plate), 'num_deaths', 'centroids_before_exclude', 'centroids_after_exclude', 'centroids_origin', 'plate', 'nfiles', 'imshifts');
