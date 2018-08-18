load G7.mat;

finterval = 4;
tolerance_diedrate = 0.9;
tolerance_havingdiedrate = 0.5;

manager_bw = ImageManager(mmts_bw, finterval + 1);
