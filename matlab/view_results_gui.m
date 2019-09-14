function varargout = view_results_gui(varargin)
% VIEW_RESULTS_GUI MATLAB code for view_results_gui.fig
%      VIEW_RESULTS_GUI, by itself, creates a new VIEW_RESULTS_GUI or raises the existing
%      singleton*.
%
%      H = VIEW_RESULTS_GUI returns the handle to a new VIEW_RESULTS_GUI or the handle to
%      the existing singleton*.
%
%      VIEW_RESULTS_GUI('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in VIEW_RESULTS_GUI.M with the given input arguments.
%
%      VIEW_RESULTS_GUI('Property','Value',...) creates a new VIEW_RESULTS_GUI or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before view_results_gui_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to view_results_gui_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help view_results_gui

% Last Modified by GUIDE v2.5 11-Sep-2019 14:08:20

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @view_results_gui_OpeningFcn, ...
                   'gui_OutputFcn',  @view_results_gui_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before view_results_gui is made visible.
function view_results_gui_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to view_results_gui (see VARARGIN)

% Choose default command line output for view_results_gui
handles.output = hObject;

params;
load(fullfile(outdir, [plate, '.out.mat']));
nfiles = min(nfiles,maxnfiles);
numdeaths = nan(1,nfiles);
for i = 1:nfiles; numdeaths(i) = sum(fdies{i}); end
numdeaths(isnan(numdeaths)) = 0;
numalive = cumsum(numdeaths);
numalive = numalive(end) - numalive;
% filenames = cell(size(dirnames));
% for i = 1:length(dirnames)
%     filenames{i} = fullfile(outdir, plate, [dirnames{i}, suffix]);
% end

[rcurve, rctds] = result_rcurve(centroids, rddetect);

handles.plate = plate;
handles.numdeaths = numdeaths;
handles.numalive = numalive;
handles.centroids = centroids;
handles.fdies = fdies;
handles.fdead = fdead;
handles.nfiles = nfiles;
handles.dirnames = dirnames;
handles.imshifts = imshifts;
handles.current = 0;
handles.playing = false;
handles.timer = [];
handles.roi = nan;
handles.rcurve = rcurve;
handles.rctds = rctds;

% Update handles structure
guidata(hObject, handles);

figure(1);
plot(numalive);
xlabel('frame');
ylabel('alive worms');

% UIWAIT makes view_results_gui wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = view_results_gui_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;



function goto_edit_Callback(hObject, eventdata, handles)
% hObject    handle to goto_edit (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of goto_edit as text
%        str2double(get(hObject,'String')) returns contents of goto_edit as a double


% --- Executes during object creation, after setting all properties.
function goto_edit_CreateFcn(hObject, eventdata, handles)
% hObject    handle to goto_edit (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function info_edit_Callback(hObject, eventdata, handles)
% hObject    handle to info_edit (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of info_edit as text
%        str2double(get(hObject,'String')) returns contents of info_edit as a double


% --- Executes during object creation, after setting all properties.
function info_edit_CreateFcn(hObject, eventdata, handles)
% hObject    handle to info_edit (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in prev_btn.
function prev_btn_Callback(hObject, eventdata, handles)
% hObject    handle to prev_btn (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
goto_image(hObject, handles, handles.current - 1);


% --- Executes on button press in next_btn.
function next_btn_Callback(hObject, eventdata, handles)
% hObject    handle to next_btn (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
goto_image(hObject, handles, handles.current + 1);


% --- Executes on button press in goto_btn.
function goto_btn_Callback(hObject, eventdata, handles)
% hObject    handle to goto_btn (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
goto_image(hObject, handles, str2double(handles.goto_edit.String));

function [handles] = goto_image(hObject, handles, idx)

if ~isnan(idx) && (idx >= 1) && (idx <= handles.nfiles)
    params;
    figure(2);
    xlimval = get(gca, 'XLim');
    ylimval = get(gca, 'YLim');
    name = handles.dirnames{idx};
    platedir = handles.plate;
    if sc ~= 1
        platedir = [handles.plate, '.resize'];
        suffix = suffixsc;
    end
    img = imread(fullfile(outdir, platedir, name, [handles.plate, suffix]));
    img = image_shift(img, fliplr(int32(handles.imshifts(idx,:)*sc)));
%     if isnan(handles.roi)
%         imshow(img);
%     else
%         roi = handles.roi;
%         roi = round(roi);
%         roi = min(roi, [size(img,2),size(img,1);size(img,2),size(img,1)]);
%         roi = max(roi, [0,0;0,0]);
%         handles.roi = roi;
%         guidata(hObject, handles);
%         imshow(img(roi(1,2):roi(2,2),roi(1,1):roi(2,1)));
%     end
    imshow(img);
    if handles.current >= 1 && handles.current <= handles.nfiles
        xlim(xlimval);
        ylim(ylimval);
    end
    fdies = handles.fdies{idx};
    fdead = handles.fdead{idx};
    ctds = handles.centroids{idx};
    ctds1 = ctds(fdead,:);
    ctds2 = ctds(fdies,:);
    rctds = ctds * sc;
    rctds1 = ctds1 * sc;
    rctds2 = ctds2 * sc;
    if ~isempty(rctds)
        hold on;
        plot(rctds(:,2), rctds(:,1), '.', 'Color', [0,1,0], 'MarkerSize', 6);
        hold off;
    end
    if ~isempty(rctds1)
        hold on;
        plot(rctds1(:,2), rctds1(:,1), 'b*');
        hold off;
    end
    if ~isempty(rctds2)
        hold on;
        plot(rctds2(:,2), rctds2(:,1), 'ro');
        hold off;
    end
    name = strrep(name, '__', 'T');
    title(sprintf('%d/%d  %s', idx, handles.nfiles, name));
    handles.info_edit.String = sprintf('%d/%d  %s', idx, handles.nfiles, name);
    handles.goto_edit.String = '';
    handles.current = idx;
    guidata(hObject, handles);
end

if idx >= handles.nfiles
    handles = stop_play(hObject, handles);
end




function interval_edit_Callback(hObject, eventdata, handles)
% hObject    handle to interval_edit (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of interval_edit as text
%        str2double(get(hObject,'String')) returns contents of interval_edit as a double


% --- Executes during object creation, after setting all properties.
function interval_edit_CreateFcn(hObject, eventdata, handles)
% hObject    handle to interval_edit (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in play_button.
function play_button_Callback(hObject, eventdata, handles)
% hObject    handle to play_button (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if handles.playing; handles = stop_play(hObject, handles);
else; handles = start_play(hObject, handles); end
guidata(hObject, handles);

function [handles] = start_play(hObject, handles)
handles.playing = true;
if isempty(handles.timer)
    handles = play_step(hObject, handles);
end
guidata(hObject, handles);

function [handles] = stop_play(hObject, handles)
handles.playing = false;
if ~isempty(handles.timer)
    stop(handles.timer);
    delete(handles.timer);
    handles.timer = [];
end
guidata(hObject, handles);

function [handles] = play_step(hObject, handles)
if handles.playing
    handles = goto_image(hObject, handles, handles.current + 1);
end
if handles.playing
    interval = str2double(handles.interval_edit.String);
    handles.timer = timer;
    guidata(hObject, handles);
    handles.timer.StartDelay = interval / 1000;
    handles.timer.TimerFcn = @(timerObj, timerEvent) play_step(hObject, handles);
    start(handles.timer);
end



% --- Executes when user attempts to close figure1.
function figure1_CloseRequestFcn(hObject, eventdata, handles)
% hObject    handle to figure1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if ~isempty(handles) && handles.playing
    handles = stop_play(hObject, handles);
end

% Hint: delete(hObject) closes the figure
delete(hObject);


% --- Executes on button press in show_rcurve_button.
function show_rcurve_button_Callback(hObject, eventdata, handles)
% hObject    handle to show_rcurve_button (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

params;
rctds = handles.rctds;
rcurve = handles.rcurve;
figure(2);
[x,y] = ginput(1);
if isempty(x); return; end
ctd = [y,x]/sc;
dists = sqrt(sum((repmat(ctd, [size(rctds,1),1]) - rctds).^2, 2));
[mindist, mini] = min(dists);
if mindist > 150
    msgbox('Failed to match an R-curve of this point', 'Error');
    return;
end
figure(3);
plot(rcurve(mini,:));

