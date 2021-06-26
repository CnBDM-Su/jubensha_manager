import datetime
import dash_table
import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_html_components as html
import pandas as pd
import os
from datetime import date
from matplotlib import pyplot as plt
from flask import Flask
import numpy as np
import sqlite3

plt.rcParams['font.sans-serif'] = 'SimHei'
plt.rcParams['axes.unicode_minus'] = False

sqlite_conn =  sqlite3.connect("suluDB.db", check_same_thread=False)
cur = sqlite_conn.cursor()


def generate_table(dataframe):

    return dash_table.DataTable(columns=[{"name": i, "id": i, "deletable": True} for i in dataframe.columns],
                                data=dataframe.to_dict('records'), style_cell={
            'textAlign': 'center',
            'height': 'auto',
            # all three widths are needed
            # 'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
            'whiteSpace': 'normal'
        })

class sql_action:
    def nav_tab_1_search(self,name,phone):  #人员信息展示
        if name == None and phone == None:
            res = cur.execute('select * from custom_info')
            df = pd.DataFrame(res,columns=['ID','name','phone','play_num','vic_num'])
            print(df)
            return df
        elif name == None and phone != None:
            res = cur.execute("select * from custom_info where phone = %s" % (phone))
            df = pd.DataFrame(res, columns=['ID', 'name', 'phone', 'play_num', 'vic_num'])
            print(df)
            return df
        elif name != None and phone == None:
            res = cur.execute("select * from custom_info where name = %s" % (name))
            df = pd.DataFrame(res, columns=['ID', 'name', 'phone', 'play_num', 'vic_num'])
            print(df)
            return df
        elif name != None and phone != None:
            res = cur.execute("select * from custom_info where phone = %s and name = %s" % (phone,name))
            df = pd.DataFrame(res, columns=['ID', 'name', 'phone', 'play_num', 'vic_num'])
            print(df)
            return df
    def nav_tab_2_search(self,startTime,endTime):  #流水信息展示

        res = cur.execute('''
          select t.TID,t.money,b.name,t.payment,t.transac_time,c.name from transac_info t
            left join 
            (select DID,name from DM_INFO) b
            on t.DID = b.DID
            left join 
            (select SID,name from STORY_INFO) c
            on t.SID = c.SID
            where t.transac_time between '%s' and '%s'
            ''' %(startTime,endTime))
        df = pd.DataFrame(res,columns=['TID','money','dm_name','dm_payment','transac_time','story_name'])
        print(df)
        return df

    def nav_tab_3_insert_2(self,name,phone,pswd,balance):    #数据导入之导入会员信息
       # print(name,phone,pswd,balance)
        if len(phone)!=11:
            msg = '手机号格式有误，请重新输入'
        else:
            sig = cur.execute("select ID from vip_info where PHONE = '%s'" % (phone))
            ifid = None
            for row in sig:
                ifid = row[0]
            if ifid == None:
                cur.execute("insert into vip_info(NAME,PHONE,BALANCE,PASSWORD) values ('%s','%s','%s','%s')" % (name,phone,balance,pswd))
                sqlite_conn.commit()
                msg = '插入成功'
            else:
                msg = '该号码已存在'
        return msg
    def nav_tab_3_insert_3(self,name,type):    #数据导入之导入新剧本信息
        print(name,type)
        s = cur.execute("select SID from story_info where name = '%s'" % (name))
        ifid = None
        for row in s:
            ifid = row[0]
        if ifid == None:
            cur.execute("insert into story_info(name,type) values ('%s','%s')" % (name,type))
            sqlite_conn.commit()
            msg = '插入成功'
        else:
            msg = '该剧本已存在'
        return msg

    def nav_tab_3_insert_4(self,name,phone):    #数据导入之导入DM信息
        if name==None or phone== None:
            return "姓名或电话未填写"

        cur.execute("insert into dm_info(name,phone) values ('%s','%s')" % (name,phone))
        sqlite_conn.commit()
    def nav_tab_3_insert_5(self,money,story_name,person_num,dm_name,payment):    #数据导入之导入流水信息
        s = cur.execute("select SID from STORY_INFO where NAME = '%s'" % (story_name))
        print(story_name)
        sid = None
        for row in s:
            print(row[0])
            sid = row[0]
        d = cur.execute("select did from dm_info where name = '%s'" % (dm_name))
        did = None
        i = 0
        for row in d:
            did = row[0]
            i+=1
        if i>1:
            did = None
        if (sid is None) or (did is None):
            msg = "输入剧本名称或DM名字有误，请重新输入"
            return msg
        else:
            for i in range(int(person_num)):
                cur.execute("insert into TRANSAC_INFO(MONEY,SID,DID,PAYMENT,TRANSAC_TIME) values ('%s','%s','%s','%s','%s')" % (money,sid,did,payment,datetime.date.today()))
                sqlite_conn.commit()
            msg = '插入成功'
            return msg
        
    def nav_tab_3_insert_6(self,story_name,story_score,dm_name,dm_score):    #数据导入之导入评分信息
        s = cur.execute("select SID from STORY_INFO where NAME = '%s'" % (story_name))
        print(story_name)
        sid = None
        for row in s:
            print(row[0])
            sid = row[0]
        d = cur.execute("select did from dm_info where name = '%s'" % (dm_name))
        did = None
        i = 0
        for row in d:
            did = row[0]
            i+=1
        if i>1:
            did = None
        if (sid is None) or (did is None):
            msg = "输入剧本名称或DM名字有误，请重新输入"
            return msg
        else:
            for i in range(int(person_num)):
                cur.execute("insert into TRANSAC_INFO(MONEY,SID,DID,PAYMENT,TRANSAC_TIME) values ('%s','%s','%s','%s','%s')" % (money,sid,did,payment,datetime.date.today()))
                sqlite_conn.commit()
            msg = '插入成功'
            return msg
    def nav_tab_4(self,phone,password,money,input_money):    #会员付款

        ifexist = cur.execute("select name,balance from vip_info where phone = '%s' and password = '%s'" % (phone,password))
        df = pd.DataFrame(ifexist)
        if df.empty:
            msg = "手机号或密码错误"
        else:
            bal = df.iloc[0,1]
            if input_money=='':
                input_money = 0
            else:
                input_money = int(input_money)
            if money == '':
                money = 0
            else:
                money = int(money)
            if int(bal)>=money:
                if input_money == 0:
                    cur.execute("update vip_info set balance = balance - %d where phone = '%s' and password = '%s'" % (int(money),phone,password))
                    sqlite_conn.commit()
                    msg = '消费：'+str(money)+'，余额：'+ str(bal-int(money))
                elif money == 0:
                    cur.execute("update vip_info set balance = balance + %d where phone = '%s' and password = '%s'" % (int(input_money), phone, password))
                    sqlite_conn.commit()
                    msg = '成功充值：'+str(input_money)+'，余额：'+str(bal+int(input_money))
                else:
                    cur.execute("update vip_info set balance = balance + %d - %d where phone = '%s' and password = '%s'" % (int(input_money),int(money), phone, password))
                    sqlite_conn.commit()
                    msg = '消费：'+str(money)+'，成功充值：'+str(input_money)+'，余额：'+str(bal+int(input_money)-int(money))
            else:
                msg = '余额不足'
            print(msg)
        return msg


def run():

    aa = sql_action()
    #aa.nav_tab_4('137',123,20,None)


    print("** finished all configuration and start server **")


    server = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))
    server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app2 = dash.Dash(name='place2', server=server, url_base_pathname='/manager/')
    app2.layout = html.Div(children=[
        html.Div(style={'backgroundColor': '#B0C4DE'}, children=[
            html.Hr(),
            html.H1('夙鹿探案馆管理系统'),
            html.Hr(),
        ]),
        html.Div(children=[
            html.Button('流水信息展示', id='btn-nclicks-1', n_clicks=0, style={"margin-left": "20px"}),
            html.Button('数据导入', id='btn-nclicks-2', n_clicks=0, style={"margin-left": "20px"}),
            html.Button('会员付款', id='btn-nclicks-3', n_clicks=0, style={"margin-left": "20px"}),
            # html.Div(id='container-button-timestamp'),
            html.Hr()
        ]),

        html.Div([html.H3(children='* 流水数据展示'),
                  html.Div(style={'width': '22%', 'height': '100%', 'float': 'left'},
                           children=[html.H4(children='查找时间段'),
                                    dcc.DatePickerRange(
                                        id='search_time',
                                        start_date=date(2021, 6, 10),
                                        end_date_placeholder_text='Select a date!'
                                    ),

                                     ]
                           ),
                  html.Button('搜索', id='btn-nclicks-6', n_clicks=0,
                              style={'width': '15%', 'height': '100%', 'float': 'left'}),
                  html.Div(id='transaction_table', children=[''], className='predict results',
                           style={'width': '80%', 'display': 'inline-block', 'height': '50%', 'float': 'left'})],
                 id='transaction_show',
                 style={'display': 'none'}),

        # show the analysis of feature
        html.Div([
            html.H3(children='* 插入数据'),
            html.Div([
                dcc.Tabs(style={'width': '100%', 'display': 'block', 'height': '50%', 'float': 'left'},
                         id="tabs", value='tab-1', children=[
                    dcc.Tab(label='会员信息', value='tab-1'),
                    dcc.Tab(label='剧本信息', value='tab-2'),
                    dcc.Tab(label='DM信息', value='tab-3'),
                    dcc.Tab(label='流水信息', value='tab-4'),
                    dcc.Tab(label='评分信息', value='tab-5'),
                ]),
                html.Div(id='tabs-content')
            ]),
            ], id='insert_data',
            style={'display': 'none'}),

        # show the training of model
        html.Div([
            html.H3(children='* 会员结算'),
            html.Div([
                html.Div(style={'width': '22%', 'height': '100%', 'float': 'left'},
                         children=[html.H4(children='输入会员手机号'),
                                   dcc.Input(id='input_vip_num', placeholder='输入会员手机号', type='text', value='',
                                             style={'width': '100%', 'height': '100%', 'float': 'left'}),
                                   ]
                         ),
                html.Div(style={'width': '22%', 'height': '100%', 'float': 'left'},
                         children=[html.H4(children='输入会员密码'),
                                   dcc.Input(id='input_vip_password', placeholder='输入会员密码', type='text', value='',
                                             style={'width': '100%', 'height': '100%', 'float': 'left'}),
                                   ]
                         ),
                html.Div(style={'width': '22%', 'height': '100%', 'float': 'left'},
                         children=[html.H4(children='输入消费金额'),
                                   dcc.Input(id='input_vip_cost', placeholder='输入消费金额', type='text', value='',
                                             style={'width': '100%', 'height': '100%', 'float': 'left'}),
                                   ]
                         ),
                html.Div(style={'width': '22%', 'height': '100%', 'float': 'left'},
                         children=[html.H4(children='输入充值金额'),
                                   dcc.Input(id='input_vip_recharge', placeholder='输入充值金额', type='text', value='',
                                             style={'width': '100%', 'height': '100%', 'float': 'left'}),
                                   ]
                         ),
                html.Button('结算', id='btn-nclicks-12', n_clicks=0,
                            style={'width': '15%', 'height': '100%', 'float': 'left'}),
                html.H3(style={'width': '100%', 'height': '50%', 'float': 'left', 'margin': '10px'},
                        children='* 结算情况'),
                html.Div(style={'width': '100%', 'height': '50%', 'float': 'left', 'margin': '10px'},id='vip_result'),
            ]),
        ], id='vip_management',
            style={'display': 'none'}),
                  ])

    @app2.callback([
                    Output('transaction_show', component_property='style'),
                    Output('insert_data', component_property='style'),
                    Output('vip_management', component_property='style')],
                   [Input('btn-nclicks-1', 'n_clicks'),
                    Input('btn-nclicks-2', 'n_clicks'),
                    Input('btn-nclicks-3', 'n_clicks')])
    def display_click(btn1, btn2, btn3):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        print(1)
        if 'btn-nclicks-1' in changed_id:
            msg = 'Button 1 was most recently clicked'
            return {'display': 'block'}, {'display': 'none'}, {'display': 'none'}
        elif 'btn-nclicks-2' in changed_id:
            msg = 'Button 2 was most recently clicked'
            return {'display': 'none'}, {'display': 'block'}, {'display': 'none'}
        elif 'btn-nclicks-3' in changed_id:
            msg = 'Button 3 was most recently clicked'
            return {'display': 'none'}, {'display': 'none'}, {'display': 'block'}
        else:
            msg = 'None of the buttons have been clicked yet'
            return {'display': 'none'}, {'display': 'none'}, {'display': 'none'}

    @app2.callback([Output("transaction_table", "children")],
                  [Input('search_time', 'start_date'),
                   Input('search_time', 'end_date'),
                   Input('btn-nclicks-6', 'n_clicks')])
    def show_transaction_table(value1, value2, btn):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if 'btn-nclicks-6' in changed_id:
            data = aa.nav_tab_2_search(value1,value2)
            print(generate_table(data))
            return [generate_table(data)]

    @app2.callback([Output('vip_result', 'children')],
                  [Input('input_vip_num', 'value'),
                   Input('input_vip_password', 'value'),
                   Input('input_vip_cost', 'value'),
                   Input('input_vip_recharge', 'value'),
                   Input('btn-nclicks-12', 'n_clicks')])
    def single_feature_analysis(value1, value2, value3, value4, btn):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if 'btn-nclicks-12' in changed_id:
            msg = aa.nav_tab_4(value1, value2, value3, value4)
            print(msg)
            return [msg]
        return ['等待结算']

    @app2.callback(Output('tabs-content', 'children'),
                  Input('tabs', 'value'))
    def render_content(tab):
        if tab == 'tab-1':
            return html.Div([
                html.H3('插入新会员信息'),
                html.Div([
                    html.H5('姓名'),
                    dcc.Input(id='t1_f1', placeholder='姓名', type='text', value='',
                              style={'width': '100%', 'height': '100%', 'float': 'left'})]),
                html.Div([
                    html.H5('电话'),
                    dcc.Input(id='t1_f2', placeholder='电话', type='text', value='',
                              style={'width': '100%', 'height': '100%', 'float': 'left'})]),
                html.Div([
                    html.H5('密码'),
                    dcc.Input(id='t1_f3', placeholder='密码', type='text', value='',
                              style={'width': '100%', 'height': '100%', 'float': 'left'})]),
                html.Div([
                    html.H5('充值金额'),
                    dcc.Input(id='t1_f4', placeholder='充值金额', type='text', value='',
                              style={'width': '100%', 'height': '100%', 'float': 'left'})]),

                html.Button('插入', id='btn-nclicks-7', n_clicks=0,
                            style={'width': '15%', 'height': '100%', 'float': 'left'}),

                html.H3(style={'width': '100%', 'height': '50%', 'float': 'left', 'margin': '10px'},
                        children='* 插入情况'),
                html.Hr(),
                html.Div(id='insert_result_1'),
                html.Hr()


            ])
        elif tab == 'tab-2':
            return html.Div([
                html.H3('插入新剧本信息'),
                html.Div([
                    html.H5('名称'),
                    dcc.Input(id='t2_f1', placeholder='名称', type='text', value='',
                              style={'width': '100%', 'height': '100%', 'float': 'left'})]),
                html.Div([
                    html.H5('类型'),
                    dcc.Input(id='t2_f2', placeholder='类型', type='text', value='',
                              style={'width': '100%', 'height': '100%', 'float': 'left'})]),

                html.Button('插入', id='btn-nclicks-8', n_clicks=0,
                            style={'width': '15%', 'height': '100%', 'float': 'left'}),

                html.H3(style={'width': '100%', 'height': '50%', 'float': 'left', 'margin': '10px'},
                        children='* 插入情况'),
                html.Hr(),
                html.Div(id='insert_result_2'),
                html.Hr()
            ])
        elif tab == 'tab-3':
            return html.Div([
                html.H3('插入新DM信息'),
                html.Div([
                    html.H5('姓名'),
                    dcc.Input(id='t3_f1', placeholder='姓名', type='text', value='',
                              style={'width': '100%', 'height': '100%', 'float': 'left'})]),
                html.Div([
                    html.H5('电话'),
                    dcc.Input(id='t3_f2', placeholder='电话', type='text', value='',
                              style={'width': '100%', 'height': '100%', 'float': 'left'})]),

                html.Button('插入', id='btn-nclicks-9', n_clicks=0,
                            style={'width': '15%', 'height': '100%', 'float': 'left'}),

                html.H3(style={'width': '100%', 'height': '50%', 'float': 'left', 'margin': '10px'},
                        children='* 插入情况'),
                html.Hr(),
                html.Div(id='insert_result_3'),
                html.Hr()
            ])
        elif tab == 'tab-4':
            return html.Div([
                html.H3('插入新流水信息'),
                html.Div([
                    html.H5('金额'),
                    dcc.Input(id='t4_f1', placeholder='金额', type='text', value='',
                              style={'width': '100%', 'height': '100%', 'float': 'left'})]),
                html.Div([
                    html.H5('剧本名称'),
                    dcc.Input(id='t4_f2', placeholder='剧本名称', type='text', value='',
                              style={'width': '100%', 'height': '100%', 'float': 'left'})]),
                html.Div([
                    html.H5('人次'),
                    dcc.Input(id='t4_f3', placeholder='人次', type='text', value='',
                              style={'width': '100%', 'height': '100%', 'float': 'left'})]),
                html.Div([
                    html.H5('DM名称'),
                    dcc.Input(id='t4_f4', placeholder='DM名称', type='text', value='',
                              style={'width': '100%', 'height': '100%', 'float': 'left'})]),
                html.Div([
                    html.H5('提成率'),
                    dcc.Input(id='t4_f5', placeholder='提成率', type='text', value='',
                              style={'width': '100%', 'height': '100%', 'float': 'left'})]),

                html.Button('插入', id='btn-nclicks-10', n_clicks=0,
                            style={'width': '15%', 'height': '100%', 'float': 'left'}),

                html.H3(style={'width': '100%', 'height': '50%', 'float': 'left', 'margin': '10px'},
                        children='* 插入情况'),
                html.Hr(),
                html.Div(id='insert_result_4'),
                html.Hr()
            ])

        elif tab == 'tab-5':
            return html.Div([
                html.H3('插入评分信息'),
                html.Div([
                    html.H5('剧本名'),
                    dcc.Input(id='t5_f1', placeholder='剧本名', type='text', value='',
                              style={'width': '100%', 'height': '100%', 'float': 'left'})]),
                html.Div([
                    html.H5('剧本评分'),
                    dcc.Input(id='t5_f2', placeholder='剧本评分', type='text', value='',
                              style={'width': '100%', 'height': '100%', 'float': 'left'})]),
                html.Div([
                    html.H5('DM姓名'),
                    dcc.Input(id='t5_f3', placeholder='DM姓名', type='text', value='',
                              style={'width': '100%', 'height': '100%', 'float': 'left'})]),
                html.Div([
                    html.H5('DM评分'),
                    dcc.Input(id='t5_f4', placeholder='DM评分', type='text', value='',
                              style={'width': '100%', 'height': '100%', 'float': 'left'})]),

                html.Button('插入', id='btn-nclicks-11', n_clicks=0,
                            style={'width': '15%', 'height': '100%', 'float': 'left'}),

                html.H3(style={'width': '100%', 'height': '50%', 'float': 'left', 'margin': '10px'},
                        children='* 插入情况'),
                html.Hr(),
                html.Div(id='insert_result_5'),
                html.Hr()

            ])


    @app2.callback([Output("insert_result_1", "children")],
                  [Input('t1_f1', 'value'),
                   Input('t1_f2', 'value'),
                   Input('t1_f3', 'value'),
                   Input('t1_f4', 'value'),
                   Input('btn-nclicks-7', 'n_clicks')])
    def insert_t1(value1, value2, value3, value4, btn):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if 'btn-nclicks-7' in changed_id:
            aa.nav_tab_3_insert_2(value1, value2, value3, value4)
            return ['插入成功']
        return ['等待插入']
    # #
    @app2.callback([Output("insert_result_2", "children")],
                  [Input('t2_f1', 'value'),
                   Input('t2_f2', 'value'),
                   Input('btn-nclicks-8', 'n_clicks')])
    def insert_t2(value1, value2, btn):
        print('insert_t2')
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if 'btn-nclicks-8' in changed_id:
            aa.nav_tab_3_insert_3(value1, value2)
            return ['插入成功']
        return ['等待插入']

    @app2.callback([Output("insert_result_3", "children")],
                  [Input('t3_f1', 'value'),
                   Input('t3_f2', 'value'),
                   Input('btn-nclicks-9', 'n_clicks')])
    def insert_t3(value1, value2, btn):
        print('insert_t3')
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if 'btn-nclicks-9' in changed_id:
            aa.nav_tab_3_insert_4(value1, value2)
            return ['插入成功']
        return ['等待插入']

    @app2.callback([Output("insert_result_4", "children")],
                  [Input('t4_f1', 'value'),
                   Input('t4_f2', 'value'),
                   Input('t4_f3', 'value'),
                   Input('t4_f4', 'value'),
                   Input('t4_f5', 'value'),
                   Input('btn-nclicks-10', 'n_clicks')])
    def insert_t4(value1, value2, value3, value4, value5, btn):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if 'btn-nclicks-10' in changed_id:
            print('insert_t4')
            message = aa.nav_tab_3_insert_5(value1, value2, value3, value4, value5)
            return [message]
        return ['等待插入']

    @app2.callback([Output("insert_result_5", "children")],
                  [Input('t5_f1', 'value'),
                   Input('t5_f2', 'value'),
                   Input('t5_f3', 'value'),
                   Input('t5_f4', 'value'),
                   Input('btn-nclicks-11', 'n_clicks')])
    def insert_t5(value1, value2, value3, value4, btn):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if 'btn-nclicks-11' in changed_id:
            message = aa.nav_tab_3_insert_6(value1, value2, value3, value4)
            return [message]
        return ['等待插入']



    server.run(debug=True, port=5000, host='127.0.0.1',use_reloader=False)


if __name__=='__main__':
    run()