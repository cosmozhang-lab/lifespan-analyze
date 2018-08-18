manager.load(1);
manager_bw.load(1);

% Multiple frames- death judgment of C. elegans
ds1 = death_judgment(manager_bw, finterval, finterval, tolerance_diedrate);
manager_bw.next();
num_deaths = zeros(1, nfiles);
num_deaths(finterval) = ds1.num_deaths;

for fcurent2 = finterval + 1:nfiles
    fcurent1 = fcurent2 - 1;
%     ds2 = cframe_death_count(manager_bw, fcurent1,fcurent2,finterval,tolerance_diedrate,tolerance_havingdiedrate);
    ds2 = death_judgment(manager_bw, fcurent2, finterval, tolerance_diedrate);
    ds2 = death_count(ds1.bw_deaths, ds2.bw_deaths, tolerance_havingdiedrate);
    manager_bw.next();
    num_deaths(fcurent2) = ds2.num_deaths;
    ds1 = ds2;
%     L = bwlabel(bwdeaths2);
%     centroids = regionprops(L, 'Centroid');
%     figure(1);imshow(mmts(:,:,fcurent2));
%     centroid = cat(1, centroids.Centroid);
%     x = centroid(:,1);
%     y = centroid(:,2);
%     hold on;plot(x,y,'r*');
%     hold off;
%     print(sprintf('out\\%d.tiff', fcurent2), '-r300');
    fprintf('%d / %d\n', fcurent2, nfiles - finterval);
end