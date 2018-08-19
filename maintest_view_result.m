load('./out/result.mat');

files = get_file_list('plate');
files = files(end-nfiles+1:end);

numalive = cumsum(num_deaths);
numalive = numalive(end) - numalive;

plot(numalive);
