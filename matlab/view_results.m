function [] = view_results()

params;

load(fullfile(outdir, [plate, '.out.mat']));
nfiles = min(nfiles, maxnfiles);

numdeaths = numdeaths(1:nfiles);
numdeaths(isnan(numdeaths)) = 0;
numalive = cumsum(numdeaths);
numalive = numalive(end) - numalive;

% calculate statistics
statprops = result_props(numdeaths);

figure(1);
plot(double((1:nfiles)-1)/framerate, numalive);
xlabel('time (day)');
ylabel('alive worms');
text(0.02, 0.15, sprintf('Plate: %s', plate), 'units', 'normalized');
text(0.02, 0.10, sprintf('Mean: %.1f', statprops.age_mean), 'units', 'normalized');
text(0.02, 0.05, sprintf('Median: %.1f', statprops.age_mid), 'units', 'normalized');
grid on;

end