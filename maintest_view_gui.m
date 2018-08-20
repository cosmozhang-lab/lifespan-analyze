function varargout = maintest_view_gui(varargin)
% MAINTEST_VIEW_GUI MATLAB code for maintest_view_gui.fig
%      MAINTEST_VIEW_GUI, by itself, creates a new MAINTEST_VIEW_GUI or raises the existing
%      singleton*.
%
%      H = MAINTEST_VIEW_GUI returns the handle to a new MAINTEST_VIEW_GUI or the handle to
%      the existing singleton*.
%
%      MAINTEST_VIEW_GUI('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in MAINTEST_VIEW_GUI.M with the given input arguments.
%
%      MAINTEST_VIEW_GUI('Property','Value',...) creates a new MAINTEST_VIEW_GUI or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before maintest_view_gui_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to maintest_view_gui_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help maintest_view_gui

% Last Modified by GUIDE v2.5 20-Aug-2018 11:36:51

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @maintest_view_gui_OpeningFcn, ...
                   'gui_OutputFcn',  @maintest_view_gui_OutputFcn, ...
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


% --- Executes just before maintest_view_gui is made visible.
function maintest_view_gui_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to maintest_view_gui (see VARARGIN)

% Choose default command line output for maintest_view_gui
handles.output = hObject;

load_params;
load('./out/result.mat');
handles.nfiles = nfiles;
filelist_saving_name = './out/filelist.mat';
if exist(filelist_saving_name, 'file')
    filelist = load(filelist_saving_name);
    filelist = filelist.filelist;
else
    filelist = get_file_list(plate);
    filelist = filelist(end-nfiles+1:end);
    save(filelist_saving_name, 'filelist');
end
handles.files = filelist;
handles.centroids = centroids_after_exclude;
handles.centroids_ori = centroids_origin;
handles.imshifts = imshifts;

handles.status_text.String = '';
handles.input_go.String = '';

numalive = cumsum(num_deaths);
numalive = numalive(end) - numalive;
figure(1);
plot(numalive);

% Update handles structure
guidata(hObject, handles);

goto_image(hObject, handles, 1);

% UIWAIT makes maintest_view_gui wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = maintest_view_gui_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on button press in button_prev.
function button_prev_Callback(hObject, eventdata, handles)
% hObject    handle to button_prev (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
goto_image(hObject, handles, handles.current - 1);


% --- Executes on button press in button_next.
function button_next_Callback(hObject, eventdata, handles)
% hObject    handle to button_next (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
goto_image(hObject, handles, handles.current + 1);


% --- Executes on button press in button_go.
function button_go_Callback(hObject, eventdata, handles)
% hObject    handle to button_go (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
goto_image(hObject, handles, str2num(handles.input_go.String));

function goto_image(hObject, handles, idx)
% hObject    handle to next_button (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
files = handles.files;
nfiles = handles.nfiles;
handles.current = idx;
thefile = files(idx);
im = imread(thefile.fullpath);
im = image_shift(im, handles.imshifts(idx,:));
% axes(handles.theaxes);
figure(2);
imshow(im);
ctds = handles.centroids{idx};
ctdsori = handles.centroids_ori{idx};
if ~isempty(ctds)
    hold on;
    plot(ctds(:,1), ctds(:,2), 'r*');
    hold off;
end
if ~isempty(ctdsori)
    hold on;
    plot(ctdsori(:,1), ctdsori(:,2), 'bo');
    hold off;
end
handles.text_status.String = replace(sprintf('%3d/%-3d %s', idx, nfiles, thefile.subdir), '__', ' ');
guidata(hObject, handles);



function input_go_Callback(hObject, eventdata, handles)
% hObject    handle to input_go (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of input_go as text
%        str2double(get(hObject,'String')) returns contents of input_go as a double


% --- Executes during object creation, after setting all properties.
function input_go_CreateFcn(hObject, eventdata, handles)
% hObject    handle to input_go (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function text_status_Callback(hObject, eventdata, handles)
% hObject    handle to text_status (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of text_status as text
%        str2double(get(hObject,'String')) returns contents of text_status as a double


% --- Executes during object creation, after setting all properties.
function text_status_CreateFcn(hObject, eventdata, handles)
% hObject    handle to text_status (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end
