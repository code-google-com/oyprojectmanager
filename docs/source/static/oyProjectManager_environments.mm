<map version="0.9.0">
<!--To view this file, download free mind mapping software Freeplane from http://freeplane.sourceforge.net -->
<node TEXT="How should&#xa;be the environments&#xa;managed" ID="ID_1693166971" CREATED="1318842010333" MODIFIED="1318842050928">
<hook NAME="MapStyle" max_node_width="600"/>
<node TEXT="with a class&#xa;inherited from object" POSITION="left" ID="ID_72336889" CREATED="1318842092981" MODIFIED="1318842102879">
<node TEXT="hard to relate the data" ID="ID_362014785" CREATED="1318842936081" MODIFIED="1318842941524">
<node TEXT="What data" ID="ID_58768511" CREATED="1318842944454" MODIFIED="1318842949623">
<font NAME="Aharoni" SIZE="12"/>
<icon BUILTIN="help"/>
<node TEXT="available extensions" ID="ID_1836050770" CREATED="1318842964040" MODIFIED="1318842976270"/>
<node TEXT="VersionTypes" ID="ID_1434900411" CREATED="1318842978131" MODIFIED="1318842980885"/>
<node TEXT="AssetVersions created&#xa;in this environment" ID="ID_176313933" CREATED="1318842987579" MODIFIED="1318843005646"/>
</node>
</node>
</node>
<node TEXT="with a class&#xa;inherited from Base" POSITION="right" ID="ID_868816195" CREATED="1318842053595" MODIFIED="1318842063923">
<node TEXT="the environments&#xa;are barely a data class&#xa;like the others, it is mostly the&#xa;actions defined in the class" ID="ID_423668337" CREATED="1318842116120" MODIFIED="1318842558271">
<node TEXT="they define actions&#xa;instead of data" ID="ID_1549721476" CREATED="1318842133405" MODIFIED="1318842142905">
<node TEXT="save" ID="ID_395852999" CREATED="1318842150554" MODIFIED="1318842151925"/>
<node TEXT="import" ID="ID_6944875" CREATED="1318842152349" MODIFIED="1318842153847"/>
<node TEXT="export" ID="ID_1803023274" CREATED="1318842154305" MODIFIED="1318842155468"/>
<node TEXT="reference" ID="ID_965658117" CREATED="1318842156443" MODIFIED="1318842158721"/>
</node>
<node TEXT="what if we&#xa;also have data" ID="ID_941980623" CREATED="1318842164443" MODIFIED="1318842477306">
<font NAME="Aharoni" SIZE="12"/>
<icon BUILTIN="help"/>
<node TEXT="VersionTypes" ID="ID_1233842277" CREATED="1318842177072" MODIFIED="1318842241139">
<node TEXT="a nice connection&#xa;to the available&#xa;VersionTypes" ID="ID_23605739" CREATED="1318842242521" MODIFIED="1318846993947"/>
</node>
<node TEXT="Asset Versions" ID="ID_1558648337" CREATED="1318842203388" MODIFIED="1318842641025">
<node TEXT="all the versions&#xa;created in this&#xa;environment" ID="ID_1572566373" CREATED="1318842251922" MODIFIED="1318842663263">
<node TEXT="how would you retrieve it" ID="ID_536286308" CREATED="1318842620985" MODIFIED="1318842632253">
<font NAME="Aharoni" SIZE="12"/>
<icon BUILTIN="help"/>
<node TEXT="it is based on the VersionType" ID="ID_110691617" CREATED="1318842666317" MODIFIED="1318842672906"/>
<node TEXT="multiple environments can have the same version" ID="ID_596533502" CREATED="1318842678786" MODIFIED="1318842689113"/>
</node>
<node TEXT="what is the benefit of knowing it" ID="ID_208469204" CREATED="1318842729112" MODIFIED="1318842741325">
<font NAME="Aharoni" SIZE="12"/>
<icon BUILTIN="help"/>
<node TEXT="nothing" ID="ID_474583545" CREATED="1318842747026" MODIFIED="1318842749949">
<icon BUILTIN="idea"/>
</node>
</node>
</node>
</node>
<node TEXT="extensions" ID="ID_158056900" CREATED="1318842275181" MODIFIED="1318842280633">
<node TEXT="available file extensions" ID="ID_189214082" CREATED="1318842283744" MODIFIED="1318842290166"/>
<node TEXT="blob string list" ID="ID_1632300760" CREATED="1318842599064" MODIFIED="1318842602856"/>
</node>
<node TEXT="how would it be initialized" ID="ID_1346308949" CREATED="1318842311256" MODIFIED="1318842475625">
<font NAME="Aharoni" SIZE="12"/>
<icon BUILTIN="help"/>
<node TEXT="when a new project is created&#xa;the environments are going&#xa;to be created by looking at&#xa;conf.Environments settings" ID="ID_479649294" CREATED="1318842320028" MODIFIED="1318847090591"/>
<node TEXT="all the environments are going&#xa;to have polymorphic identities" ID="ID_1147173975" CREATED="1318842349347" MODIFIED="1318847109183">
<icon BUILTIN="idea"/>
<node TEXT="they will be regenerated&#xa;from that info" ID="ID_1134702510" CREATED="1318842373547" MODIFIED="1318842385730"/>
<node TEXT="and we are good to go" ID="ID_599271360" CREATED="1318842390664" MODIFIED="1318842401442"/>
<node TEXT="any environment can be&#xa;retrieved back with its&#xa;data from the database" ID="ID_1214672129" CREATED="1318842405937" MODIFIED="1318842425720">
<node TEXT="the action is going to be updated&#xa;with the module" ID="ID_720348194" CREATED="1318842434677" MODIFIED="1318842468335"/>
<node TEXT="the data is going to be updated&#xa;with the project" ID="ID_1071008631" CREATED="1318842450962" MODIFIED="1318842464363"/>
<node TEXT="self.asset, self.project, self.sequnce&#xa;is not going to be stored in the&#xa;environment instance, it is going to&#xa;be passed to the environment&#xa;instance all the time" ID="ID_1704145116" CREATED="1318847137740" MODIFIED="1318847195942"/>
</node>
</node>
</node>
<node TEXT="nice to have connections to&#xa;the other part of the data" ID="ID_1353990910" CREATED="1318842065428" MODIFIED="1318842083071"/>
</node>
</node>
<node TEXT="environments like&#xa;Maya, Houdini&#xa;Nuke should be handled&#xa;out of the system" ID="ID_468221180" CREATED="1318856263890" MODIFIED="1318856302270">
<node TEXT="it is pipeline code,&#xa;thus it is specific to&#xa;studio" ID="ID_1159024611" CREATED="1318856303860" MODIFIED="1318856335877">
<node TEXT="OYPROJECTMANAGER_PATH&#xa;environment variable" ID="ID_1746166506" CREATED="1318856340179" MODIFIED="1318856366669">
<node TEXT="conf.py" ID="ID_920675704" CREATED="1318856368997" MODIFIED="1318856371483">
<node TEXT="maya.py" ID="ID_896214317" CREATED="1318856373428" MODIFIED="1318857089150"/>
<node TEXT="houdini.py" ID="ID_257993632" CREATED="1318856378751" MODIFIED="1318857091308"/>
<node TEXT="nuke.py" ID="ID_999923563" CREATED="1318856381941" MODIFIED="1318857093497"/>
<node TEXT="photoshop.py" ID="ID_1384337898" CREATED="1318856387123" MODIFIED="1318857095400"/>
<node TEXT="3dequalizer.py" ID="ID_371110516" CREATED="1318856391316" MODIFIED="1318857098144"/>
<node TEXT="...." ID="ID_617396736" CREATED="1318857109768" MODIFIED="1318857110993"/>
<node TEXT="lower_case_environment_name.py" ID="ID_864865297" CREATED="1318856409671" MODIFIED="1318857107727"/>
</node>
</node>
</node>
</node>
</node>
</node>
</map>
