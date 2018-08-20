function varargout = view_images(varargin)
% VIEW_IMAGES MATLAB code for view_images.fig
%      VIEW_IMAGES, by itself, creates a new VIEW_IMAGES or raises the existing
%      singleton*.
%
%      H = VIEW_IMAGES returns the handle to a new VIEW_IMAGES or the handle to
%      the existing singleton*.
%
%      VIEW_IMAGES('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in VIEW_IMAGES.M with the given input arguments.
%
%      VIEW_IMAGES('Property','Value',...) creates a new VIEW_IMAGES or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before view_images_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to view_images_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help view_images

% Last Modified by GUIDE v2.5 15-Aug-2018 21:03:25

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @view_images_OpeningFcn, ...
                   'gui_OutputFcn',  @view_images_OutputFcn, ...
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


% --- Executes just before view_images is made visible.
function view_images_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to view_images (see VARARGIN)

% Choose default command line output for view_images
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);

% UIWAIT makes view_images wait for user response (see UIRESUME)
% uiwait(handles.figure1);

handles.plate_input.String = 'H12';
handles.status_text.String = '';
handles.index_input.String = '1';


% --- Outputs from this function are returned to the command line.
function varargout = view_images_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;



function index_input_Callback(hObject, eventdata, handles)
% hObject    handle to index_input (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of index_input as text
%        str2double(get(hObject,'String')) returns contents of index_input as a double


% --- Executes during object creation, after setting all properties.
function index_input_CreateFcn(hObject, eventdata, handles)
% hObject    handle to index_input (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in go_button.
function go_button_Callback(hObject, eventdata, handles)
% hObject    handle to go_button (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
goto_image(hObject, handles, str2num(handles.index_input.String));


% --- Executes on button press in prev_button.
function prev_button_Callback(hObject, eventdata, handles)
% hObject    handle to prev_button (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
nfiles = handles.nfiles;
goto_image(hObject, handles, mod(handles.current - 2, nfiles) + 1);

% --- Executes on button press in next_button.
function next_button_Callback(hObject, eventdata, handles)
% hObject    handle to next_button (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
nfiles = handles.nfiles;
goto_image(hObject, handles, mod(handles.current, nfiles) + 1);


function goto_image(hObject, handles, idx)
% hObject    handle to next_button (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
files = handles.files;
nfiles = handles.nfiles;
handles.current = idx;
thefile = files(idx);
im = imread(thefile.fullpath);
axes(handles.image_axes);
imshow(im);
handles.status_text.String = replace(sprintf('%3d/%-3d %s', idx, nfiles, thefile.subdir), '__', ' ');
guidata(hObject, handles);


function plate_input_Callback(hObject, eventdata, handles)
% hObject    handle to plate_input (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of plate_input as text
%        str2double(get(hObject,'String')) returns contents of plate_input as a double


% --- Executes during object creation, after setting all properties.
function plate_input_CreateFcn(hObject, eventdata, handles)
% hObject    handle to plate_input (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in load_button.
function load_button_Callback(hObject, eventdata, handles)
% hObject    handle to load_button (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

main_params;

plate = handles.plate_input.String;
if ~isempty(plate)
    files = get_file_list(plate);
    nfiles = length(files);
    handles.files = files;
    handles.nfiles = nfiles;
    handles.current = 0;
    handles.status_text.String = sprintf('0 / %d', nfiles);
    axes(handles.image_axes);
    cla(handles.image_axes,'reset');
    guidata(hObject, handles);
end



function status_text_Callback(hObject, eventdata, handles)
% hObject    handle to status_text (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of status_text as text
%        str2double(get(hObject,'String')) returns contents of status_text as a double


% --- Executes during object creation, after setting all properties.
function status_text_CreateFcn(hObject, eventdata, handles)
% hObject    handle to status_text (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end
