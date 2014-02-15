<map version="0.9.0">
<!--To view this file, download free mind mapping software Freeplane from http://freeplane.sourceforge.net -->
<node TEXT="version paths&#xa;should it be&#xa;relative&#xa;or&#xa;absolute" ID="ID_558430202" CREATED="1324973594083" MODIFIED="1324973614285">
<hook NAME="MapStyle" max_node_width="600"/>
<node TEXT="relative" POSITION="right" ID="ID_1873037331" CREATED="1324973616703" MODIFIED="1324973619991">
<node TEXT="it completely the decision of&#xa;the studio" ID="ID_1074411951" CREATED="1324974482650" MODIFIED="1324974500909">
<node TEXT="to be consistent the fullpath&#xa;should only join&#xa;path and filename" ID="ID_1637030343" CREATED="1324974518351" MODIFIED="1324974543619">
<node TEXT="then the studio itself should&#xa;also join the project if it is&#xa;using a relative path scheme" ID="ID_1998057842" CREATED="1324974546941" MODIFIED="1324974569549"/>
</node>
</node>
<node TEXT="easy to manage when&#xa;the project restored&#xa;from backup&#xa;and the paths are changed" ID="ID_1337884221" CREATED="1324973625507" MODIFIED="1324974434044">
<node TEXT="a query to find the versions&#xa;related to this project and&#xa;replacing the path can solve this" ID="ID_617178858" CREATED="1324974435290" MODIFIED="1324974477083"/>
</node>
<node TEXT="path changes will not effect&#xa;version placements" ID="ID_491129828" CREATED="1324973649154" MODIFIED="1324973663788">
<node TEXT="they are all calculated&#xa;by joining the project.fullpath&#xa;with the path value" ID="ID_1604838160" CREATED="1324973665099" MODIFIED="1324973690794">
<node TEXT="can it be done in a way&#xa;by checking if the path&#xa;is absolute or relative&#xa;and then joining it with&#xa;the project path if it is&#xa;relative" ID="ID_927068343" CREATED="1324973695614" MODIFIED="1324973729415"/>
</node>
</node>
</node>
<node TEXT="absolute" POSITION="left" ID="ID_1762654333" CREATED="1324973621581" MODIFIED="1324973623986">
<node TEXT="it is consistent to have absolute paths" ID="ID_1622627621" CREATED="1324974576140" MODIFIED="1324974586108"/>
<node TEXT="having a project relative path and then&#xa;a workspace relative path is&#xa;making things unneccessarly complex" ID="ID_635496159" CREATED="1324974588301" MODIFIED="1324974626865"/>
</node>
<node TEXT="both relative&#xa;or absolute" POSITION="right" ID="ID_1825697637" CREATED="1325160410384" MODIFIED="1325160446121">
<node TEXT="this way it is depending to&#xa;the VersionType templates" ID="ID_1902000485" CREATED="1325160428400" MODIFIED="1325160460610">
<node TEXT="if the template is absolute&#xa;then the path is also absolute" ID="ID_329711411" CREATED="1325160462039" MODIFIED="1325161105571"/>
<node TEXT="if the template is relative&#xa;the the path is also relative" ID="ID_335014298" CREATED="1325161083454" MODIFIED="1325161099218"/>
</node>
<node TEXT="Problems of this" ID="ID_1700777053" CREATED="1325161953263" MODIFIED="1325161969424">
<node TEXT="The project doesn&apos;t have&#xa;a fullpath attribute stored in the DB" ID="ID_1858172444" CREATED="1325161970345" MODIFIED="1325162003385">
<node TEXT="Version has a fullpath in DB" ID="ID_1456628084" CREATED="1325162008216" MODIFIED="1325162018254">
<node TEXT="this creates a duality" ID="ID_917044020" CREATED="1325162034612" MODIFIED="1325162039320"/>
<node TEXT="project path may change" ID="ID_541377021" CREATED="1325162041465" MODIFIED="1325162051937"/>
<node TEXT="where the version path is fixed" ID="ID_1013667457" CREATED="1325162052984" MODIFIED="1325162059863"/>
</node>
<node TEXT="Solutions" ID="ID_1686481515" CREATED="1325162067570" MODIFIED="1325162098751">
<node TEXT="add fullpath to project and fix it if the path changes" ID="ID_1184265644" CREATED="1325162111750" MODIFIED="1325162126184">
<node TEXT="also fix version paths&#xa;by replacing the proejct.fullpath part&#xa;with the new one" ID="ID_1998519231" CREATED="1325162129963" MODIFIED="1325162156979"/>
</node>
<node TEXT="do not care about it" ID="ID_876193084" CREATED="1325162163193" MODIFIED="1325162168878">
<node TEXT="use a fixed projects path all the time" ID="ID_1808439894" CREATED="1325162171965" MODIFIED="1325162187201"/>
<node TEXT="or fix it when a problem arise" ID="ID_1596332217" CREATED="1325162191926" MODIFIED="1325162201820"/>
</node>
</node>
</node>
</node>
</node>
<node TEXT="stored as relative&#xa;but returned as&#xa;absolute" POSITION="left" ID="ID_1023839357" CREATED="1325177938306" MODIFIED="1325192624217" COLOR="#ff0000">
<font NAME="Liberation Sans" SIZE="12"/>
<icon BUILTIN="idea"/>
<icon BUILTIN="bookmark"/>
<node TEXT="reasonable" ID="ID_1753055183" CREATED="1325177964291" MODIFIED="1325177967814"/>
<node TEXT="returned as an absolute path" ID="ID_303839471" CREATED="1325178088298" MODIFIED="1325178095135"/>
<node TEXT="stored in database as relative" ID="ID_566593923" CREATED="1325178080998" MODIFIED="1325178087724"/>
<node TEXT="path values calculated onece" ID="ID_1427229591" CREATED="1325178069830" MODIFIED="1325178080239"/>
<node TEXT="path" ID="ID_322537164" CREATED="1325178117448" MODIFIED="1325178122839"/>
<node TEXT="output" ID="ID_500877927" CREATED="1325178125153" MODIFIED="1325178127292"/>
<node TEXT="fullpath" ID="ID_1629648023" CREATED="1325178127992" MODIFIED="1325178130449"/>
</node>
</node>
</map>
