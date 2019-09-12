# -*- coding: utf-8 -*-
"""
Created on Sun Mar 28 09:36:40 2010

@author: Ludovic Autin - ludovic.autin@gmail.com
"""
import bpy

bl_info = {
    "name": "ePMV synchro",
    "description": """synchronise epmv data with blender geometry in realtime.""",
    "author": "Ludovic Autin",
    "version": (0,3,7),
    "blender": (2, 8, 0),
    "api": 31236,
    #"location": "View3D > Tool Shelf > ePMV",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": ""\
        "Scripts/My_Script",
    "tracker_url": ""\
        "func=detail&aid=<number>",
    "category": "System"}


class ModalTimerEPMVUpdateOperator(bpy.types.Operator):
    '''Operator which runs its self from a timer.'''
    bl_idname = "epmv.synchro"
    bl_label = "ePMV Synchro"

    _timer = 0

    def modal(self, context, event):
        if event.type == 'ESC':
            return self.cancel(context)

        if event.type == 'TIMER':
            # change theme color, silly!
            color = context.user_preferences.themes[0].view_3d.back
            color.s = 1.0
            color.h += 0.01
            #get epmv
            epmv = bpy.mv.values()[0]
            #how do I get epmv...
            sc=epmv.helper.getCurrentScene()
            if epmv.synchro_timeline : 
                traj = epmv.gui.current_traj
                epmv.updateData(traj,_timer)
                _timer+=1
                #getCurrent time
            ##    t = self.timeControl.currentTime()
            ##    frame = int(t.asUnits(OpenMaya.MTime.kFilm))
            ##            frame=doc.GetTime().GetFrame(fps)
            #    st,ft=self.epmv.synchro_ratio
            #    if (frame % ft) == 0:   
            #        step = frame * st
            #        self.epmv.updateData(traj,step)
            else :
                #get selected object
                slist = epmv.helper.getCurrentSelection()
                if not slist : 
                   #do nothing
                   pass
                else :
                    for l in slist:
                        print(l)
                    epmv.updateCoordFromObj(slist,debug=True)
        return {'PASS_THROUGH'}

    def execute(self, context):
        context.window_manager.modal_handler_add(self)
        self._timer = context.window_manager.event_timer_add(0.1, context.window)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        return {'CANCELLED'}


def register():
    bpy.utils.register_class(ModalTimerEPMVUpdateOperator)


def unregister():
    bpy.utils.unregister_class(ModalTimerEPMVUpdateOperator)


if __name__ == "__main__":
    register()
    # test call
    #bpy.ops.epmv.synchro()

