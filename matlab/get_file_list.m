function [ files ] = get_file_list( plate_name )

main_params;

plate_filename = [plate_name, imgsuffix];
subdirs = dir(rootdir);
for i = 1:length(subdirs)
    if isempty(regexp(subdirs(i).name, '\d{4}\-\d{2}\-\d{2}__\d{2}\-\d{2}\-\d{2}', 'ONCE'))
        subdirs(i).isdir = 0;
    end
end
tmp = cell(1,length(subdirs));
cnt = 0;
for i = 1:length(subdirs)
    if subdirs(i).isdir
        files_in_subdir = dir(fullfile(rootdir, subdirs(i).name));
        for j = 1:length(files_in_subdir)
            if strcmp(files_in_subdir(j).name, plate_filename)
                tmpstruct = struct();
                tmpstruct.fullpath = fullfile(rootdir, subdirs(i).name, files_in_subdir(j).name);
                tmpstruct.subdir = subdirs(i).name;
                tmp{i} = tmpstruct;
                cnt = cnt + 1;
            end
        end
    end
end
files = struct;
ii = 1;
for i = 1:length(tmp)
    if ~isempty(tmp{i})
        files(ii).fullpath = tmp{i}.fullpath;
        files(ii).subdir = tmp{i}.subdir;
        ii = ii + 1;
    end
end

end

