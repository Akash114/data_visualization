from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from . import Form
import pandas as pd
import json
import itertools
import numpy as np
from faker import Factory


colorPalette = ['#55efc4', '#81ecec', '#a29bfe', '#ffeaa7', '#fab1a0', '#ff7675', '#fd79a8']
colorPrimary, colorSuccess, colorDanger = '#79aec8', colorPalette[0], colorPalette[5]


#Home page
def home(request):
    form = Form.FileUploadForm()
    return render(request, 'visualization.html', {'form': form})


def read_file(request):
    file = request.FILES["Select_File"]
    try:
        df = pd.read_excel(file)
    except:
        try:
            df = pd.read_csv(file)
        except:
            return HttpResponse(json.dumps({'msg': 'File type is not supported!'}),
                                content_type="application/json")
    return df


#Get the column name from first raw
def get_columns(request):
    if request.method == 'POST':
        form = Form.FileUploadForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            df = read_file(request)
            column = list(df.columns)
            return HttpResponse(json.dumps({'data': column, 'msg': 'File Uploaded'}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'msg': form.errors}), content_type="application/json")


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


def visualize(request):
    if request.method == 'POST':
        form = Form.FileUploadForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            df = read_file(request)
            column = request.POST['columns']
            data_dict = dict(df[column].value_counts())

            data = dict(sorted(data_dict.items(), key=lambda x: x[1], reverse=True))

            data = {k: v for k, v in data.items() if k == k}

            #First 20 results
            if len(data) > 20:
                data = dict(itertools.islice(data.items(), 20))
            return HttpResponse(json.dumps({
                'title': f' {column}',
                'data': {
                    'labels': list(data.keys()),
                    'backgroundColor': colorPrimary,
                    'borderColor': colorPrimary,
                    'data': list(data.values()),
                },
            }, cls=NpEncoder), content_type="application/json")
        return HttpResponse(json.dumps({'msg': 'Something went wrong!'}), content_type="application/json")
    return HttpResponse(json.dumps({'msg': 'Something went wrong!'}), content_type="application/json")


def two_variables(request):
    if request.method == 'POST':
        fake = Factory.create()
        form = Form.FileUploadForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            df = read_file(request)
            column = request.POST['columns']
            column2 = request.POST['columns2']
            district = list(df[column].unique())
            data = {}
            for i in district:
                df_final = df[df[column] == i]
                data[i] = dict(df_final[column2].value_counts())

            #second variables dataset
            final_data = {}
            for i in df[column2].unique():
                l = []
                for j in data:
                    try:
                        l.append(data[j][i])
                    except:
                        l.append(0)
                final_data[i] = l

            #Removing None Values
            final_data = {k: v for k, v in final_data.items() if k == k}

            dataset = []
            for key in final_data:
                dic = {'label': key, 'backgroundColor': fake.hex_color(), 'borderColor': '#79AEC8',
                       'data': final_data[key]}
                dataset.append(dic)
            return JsonResponse({
                'title': f' {column}',
                'data': {
                    'labels': list(data.keys()),
                    'dataset': dataset
                },
            }, encoder=NpEncoder)
