function [num_deaths2,bwdeaths2] = cframe_death_count(bw_manager, fcurent1,fcurent2,finterval,tolerance_diedrate,tolerance_havingdiedrate)
% ***************************************************************************
% Function: Calculate the deaths of C. elegans in the current frame.(Not include having died)
%   Input:
%             bw_manager: ImageManager
%             fcurent1: The last frame
%             fcurent2: The curent frame
%             finterval: The time interval for judging death. The default is 4.
%             tolerance_diedrate: The criteria for judging death(died), defined as overlapping area ratio. The default is 0.9.
%             tolerance_havingdiedrate:The criteria for judging death(having died), defined as overlapping area ratio. The default is 0.5.
%   Output:
%             num_deaths2: The death for curent frame
%             bwdeaths2: 2-D binary image defined as the dead C. elegans for curent frame
% Author: Zhe Zhang
% Date: 2018/8/16
% ***************************************************************************

[num_deaths1_ori,bwdeaths1_ori] = death_judgment(bw_manager,fcurent1,finterval,tolerance_diedrate);
[num_deaths2_ori,bwdeaths2_ori] = death_judgment(bw_manager,fcurent2,finterval,tolerance_diedrate);

% [num_deaths2,bwdeaths2] = death_count(bwdeaths1_ori,bwdeaths2_ori,num_deaths2_ori,tolerance_havingdiedrate);

num_deaths2 = 1; bwdeaths2 = 1;

% % show
% slice1 = uint8(bwdeaths1_ori *125);
% slice2 = uint8(bwdeaths2_ori *125);
% imagesc(merge_image(slice1, slice2, [])); axis equal;
