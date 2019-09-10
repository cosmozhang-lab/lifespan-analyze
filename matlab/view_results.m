function [] = view_results()

params;

load(fullfile(outdir, [plate, '.out.mat']));
nfiles = min(nfiles, maxnfiles);

%% calculate number of deaths

numdeaths = nan(1,nfiles);
for i = 1:nfiles; numdeaths(i) = sum(fdies{i}); end
numdeaths = numdeaths(1:nfiles);
numdeaths(isnan(numdeaths)) = 0;
numalive = cumsum(numdeaths);
numalive = numalive(end) - numalive;

%% calculate statistics

% statprops = result_props(numdeaths);
% 
% figure(1);
% xseries = double((1:nfiles)-1)/framerate;
% plot(xseries, numalive);
% xlabel('time (day)');
% ylabel('alive worms');
% xlim(xseries([1,end]));
% text(0.02, 0.15, sprintf('Plate: %s', plate), 'units', 'normalized');
% text(0.02, 0.10, sprintf('Mean: %.1f', statprops.age_mean), 'units', 'normalized');
% text(0.02, 0.05, sprintf('Median: %.1f', statprops.age_mid), 'units', 'normalized');
% grid on;

%% registrate dead worms and withdraw their IoU value series

rcurve = [];
rctds = [];
for i = 1:nfiles
    ctds = centroids{i};
    fds = fdead{i};
    dctds = ctds(fds, :);
    for j = 1:size(dctds,1)
        if isempty(rctds)
            rctds = dctds(i,:);
            rcurve = nan(1,nfiles);
            rcurve(1,i) = fds;
            continue;
        end
        dists = sqrt(sum((repmat(dctds(j,:), [size(rctds,1),1]) - rctds) .^ 2, 2));
        [~,k] = min(dists);
        if dists(k) < 20
        else
            rctds = [rctds;dctds(j,:)];
            rcurve = [rcurve;nan(1,nfiles)];
            rcurve(end,i) = rddetect(i);
        end
    end
end

end