# Sample live_script
from UM.Message import Message
from UM.Settings.SettingInstance import SettingInstance
from cura.CuraApplication import CuraApplication
from UM.Settings.SettingInstance import SettingInstance
from UM.Resources import Resources

selection_pass = CuraApplication.getInstance().getRenderer().getRenderPass("selection")
global_container_stack = CuraApplication.getInstance().getGlobalContainerStack()
plugin_enabled = global_container_stack.setProperty("support_mesh", True)