from PyInstaller.__main__ import run

if __name__ == '__main__':
    #设置参数——携程数组，最后一个是入口文件，#'--hidden-import'就是隐式导入的包
    opts = ['-D',
            '--hidden-import', 'dash',
            '--hidden-import', 'dash_table',
            '--hidden-import', 'dash_core_components',
            '--hidden-import', 'dash.dependencies',
            '--hidden-import', 'dash_html_components',
            '--hidden-import', 'pandas',
            '--hidden-import', 'matplotlib',
            '--hidden-import', 'flask',
            '--hidden-import', 'datetime',
            '--clean',
            'test.py']
    #执行run函数
    run(opts)