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

% Last Modified by GUIDE v2.5 20-Oct-2018 11:48:56

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
numdeaths(isnan(numdeaths)) = 0;
numalive = cumsum(numdeaths);
numalive = numalive(end) - numalive;
% filenames = cell(size(dirnames));
% for i = 1:length(dirnames)
%     filenames{i} = fullfile(outdir, plate, [dirnames{i}, suffix]);
% end

handles.plate = plate;
handles.numdeaths = numdeaths;
handles.numalive = numalive;
handles.centroids = centroids;
handles.oricentroids = oricentroids;
handles.nfiles = length(dirnames);
handles.dirnames = dirnames;
handles.imshifts = imshifts;
handles.current = 0;

% Update handles structure
guidata(hObject, handles);

figure(1);
plot(numalive);

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

function goto_image(hObject, handles, idx)

if ~isnan(idx) && (idx >= 0) && (idx <= handles.nfiles)
    params;
    figure(2);
    name = handles.dirnames{idx};
    img = imread(fullfile(outdir, handles.plate, [name, suffix]));
    imshow(image_shift(img, fliplr(handles.imshifts(idx,:))));
    ctds = handles.centroids{idx};
    octds = handles.oricentroids{idx};
    if ~isempty(octds)
        hold on;
        plot(octds(:,2), octds(:,1), 'b*');
        hold off;
    end
    if ~isempty(ctds)
        hold on;
        plot(ctds(:,2), ctds(:,1), 'ro');
        hold off;
    end
    name = strrep(name, '__', 'T');
    title(sprintf('%d/%d  %s', idx, handles.nfiles, name));
    handles.info_edit.String = sprintf('%d/%d  %s', idx, handles.nfiles, name);
    handles.goto_edit.String = '';
    handles.current = idx;
    guidata(hObject, handles);
end

