%manager.load(1);
manager_bw.load(1);

% Multiple frames- death judgment of C. elegans
ds1 = death_judgment(manager_bw, finterval, finterval, tolerance_diedrate);
manager_bw.next();
num_deaths = zeros(1, nfiles);
num_deaths(finterval) = ds1.num_deaths;
centroids = cell(1, nfiles);

for fcurent2 = finterval + 1:nfiles
    fcurent1 = fcurent2 - 1;
    ds2 = death_judgment(manager_bw, fcurent2, finterval, tolerance_diedrate);
    ds2 = death_count(ds1.bw_deaths, ds2.bw_deaths, tolerance_havingdiedrate);
    manager_bw.next();
    num_deaths(fcurent2) = ds2.num_deaths;
    centroids{fcurent2} = ds2.centroids;
    ds1 = ds2;
    fprintf('%d / %d\n', fcurent2, nfiles);
end

save('./out/result.mat', 'num_deaths', 'centroids', 'plate', 'nfiles');
