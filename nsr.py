#!V:\Programs\Side Effects Software\Houdini 15.5.607\bin\hython.exe

import os
import hou
import glob
import ConfigParser as CP

'''

output_format:
    PROJECT_NAME.ROP_NODE_NAME.FRAME.EXTENSION

Cache files must have full path

'''
conf = CP.ConfigParser()
conf.read('toRender.cfg')
HOUDINI_FOLDER = "E:\Videos\Houdini"
CHOUDINI_FOLDER = "C:\Houdini"


def get_last_frame(project_directory, END_FRAME, rop_node):
    _ = glob.glob("{}\\*.{}.*".format(project_directory, rop_node))
    if not _:
        return 1  # nothing was rendered yet
    try:
        frame_nums = sorted([int(file.split('.')[2]) for file in _])
    except ValueError as e:
        print("Getting last frame in {} failed with msg: {}".format(rop_node, e))
        return 0

    for frame in frame_nums:
        if int(frame) >= END_FRAME:
            return None
    return int(frame)


def render(PROJECT_NAME, RENDER_FOLDER, frame, extension, rop_node):
    render_node = hou.node("/out/{}".format(rop_node))
    operator_name = render_node.name()
    # Defines main take so it can set the frame range
    main_take = hou.takes.takes()[-1]
    if hou.takes.currentTake().name() is not "Main":
        hou.takes.setCurrentTake(main_take)
    render_node.parm('trange').set(1)

    if extension is None:
        extension = render_node.parm("vm_device").eval()
    path = "{}\\{}.{}.{}.{}".format(
        RENDER_FOLDER, PROJECT_NAME, operator_name, frame, extension)

    if os.path.isdir(RENDER_FOLDER) is False:
        try:
            os.makedirs(RENDER_FOLDER)
        except OSError as e:
            print("Error creating directory: {}".format(e))
            return

    render_node.render(frame_range=(frame, frame),
                       output_file=path, verbose=True, output_progress=False)


def main():
    for project in conf.sections():
        try:
            PROJECT_NAME = conf.get(project, 'project_name')
        except CP.NoOptionError:
            raise "No project name"

        try:
            HIP_EXTENSION = conf.get(project, 'hip_extension')
        except CP.NoOptionError:
            HIP_EXTENSION = 'hip'

        try:
            OUT_EXTENSION = conf.get(project, 'rop_extension')
        except CP.NoOptionError:
            OUT_EXTENSION = None  # Uses default defined in the ROP node, defined in func render

        try:
            CACHE_EXTENSION = conf.get(project, 'cache_extension')
        except CP.NoOptionError:
            CACHE_EXTENSION = 'bgeo.sc'

        try:
            ROP_NODES = [node.strip()
                         for node in conf.get(project, 'rop_nodes').split(',')]
        except CP.NoOptionError:
            # Uses default defined in the ROP node, defined in func render
            ROP_NODES = []

        try:
            CACHE_NODES = [node.strip()
                           for node in conf.get(project, 'cache_nodes').split(',')]
        except CP.NoOptionError:
            CACHE_NODES = []

        HIPFILE = "{}\\{}\\{}.{}".format(
            HOUDINI_FOLDER, PROJECT_NAME, PROJECT_NAME, HIP_EXTENSION)

        try:
            hou.hipFile.load(HIPFILE)
        except hou.OperationFailed as e:
            return "Not possible to load file {} - {}".format(HIPFILE, e)

        RENDER_FOLDER = "{}\\{}\\render".format(HOUDINI_FOLDER, PROJECT_NAME)

        END_FRAME = int(conf.get(project, 'end_frame'))

        for cache_node in CACHE_NODES:
            CCACHE = "{}\\{}\\{}".format(
                CHOUDINI_FOLDER, PROJECT_NAME, cache_node)
            START_FRAME = get_last_frame(CCACHE, END_FRAME, cache_node)
            if START_FRAME:
                for frame in range(START_FRAME, END_FRAME + 1):
                    render(PROJECT_NAME, CCACHE,
                           frame, CACHE_EXTENSION, cache_node)
            else:
                print("Nothing to render in {} from {}!".format(
                    cache_node, project))

        for rop_node in ROP_NODES:
            START_FRAME = get_last_frame(RENDER_FOLDER, END_FRAME, rop_node)
            if START_FRAME:
                for frame in range(START_FRAME, END_FRAME + 1):
                    render(PROJECT_NAME, RENDER_FOLDER, frame,
                           OUT_EXTENSION, rop_node)
                    pass
            else:
                print("Nothing to render in {} from {}!".format(rop_node, project))

if __name__ == "__main__":
    main()
