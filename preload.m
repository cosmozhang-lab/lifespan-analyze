plate = 'G7';
load(sprintf('./data/%s.mat', plate));

finterval = 4;
tolerance_diedrate = 0.9;
tolerance_havingdiedrate = 0.5;

manager_bw = ImageManager(mmts_bw, finterval + 1);
