function [ props ] = result_props( numdeaths )
params;
nfiles = length(numdeaths);
ages = nan(1,sum(numdeaths));
nworms = 0;
for i = 1:nfiles
    ndeath = numdeaths(i);
    for j = 1:ndeath
        nworms = nworms + 1;
        ages(nworms) = double(i-1) / double(framerate);
    end
end
age_mean = mean(ages);
age_mid = median(ages);

props = struct;
props.ages = ages;
props.age_mean = age_mean;
props.age_mid = age_mid;
end

