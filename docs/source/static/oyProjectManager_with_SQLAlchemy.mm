<map version="0.9.0">
<!--To view this file, download free mind mapping software Freeplane from http://freeplane.sourceforge.net -->
<node TEXT="oyProjectManager&#xa;with&#xa;SQLAlchemy" ID="ID_19663084" CREATED="1318081946588" MODIFIED="1318082023687" COLOR="#18898b" STYLE="fork">
<hook NAME="MapStyle" max_node_width="600"/>
<font NAME="Aharoni" SIZE="12" BOLD="true"/>
<edge STYLE="bezier" COLOR="#808080" WIDTH="thin"/>
<icon BUILTIN="idea"/>
<node TEXT="Place the metadata.db&#xa;under the project root" POSITION="right" ID="ID_533092420" CREATED="1318082133000" MODIFIED="1318082803641">
<font NAME="Aharoni" SIZE="12"/>
<icon BUILTIN="help"/>
<node TEXT="how many projects needs&#xa;more than one sequence" ID="ID_1303310257" CREATED="1318082271623" MODIFIED="1318082756197">
<node TEXT="lots of them" ID="ID_983594130" CREATED="1318082284192" MODIFIED="1318082289067"/>
</node>
<node TEXT="need to place the db&#xa;under the project" ID="ID_543561835" CREATED="1318082218486" MODIFIED="1318082751129">
<node TEXT="Hard to backup" ID="ID_1321015465" CREATED="1318082161279" MODIFIED="1318082166865"/>
<node TEXT="can not isolate the child sequences" ID="ID_1560403117" CREATED="1318082168063" MODIFIED="1318082177728"/>
<node TEXT="easy to program" ID="ID_1452156005" CREATED="1318082261636" MODIFIED="1318082270093"/>
</node>
<node TEXT="when the project needs to be&#xa;archived, there is no problem" ID="ID_1694413731" CREATED="1318083132011" MODIFIED="1318083150737">
<node TEXT="all the Sequences will be archived also" ID="ID_130145454" CREATED="1318083325218" MODIFIED="1318083334631"/>
</node>
<node TEXT="what should we do to archive&#xa;only one Sequence in a Project&#xa;with multiple Sequences" ID="ID_1293273321" CREATED="1318083154109" MODIFIED="1318083314142">
<node TEXT="archive the Sequence" ID="ID_268300944" CREATED="1318083188992" MODIFIED="1318083196019">
<node TEXT="delete the Sequence folder" ID="ID_1345904309" CREATED="1318083196956" MODIFIED="1318083207790">
<node TEXT="work with other Sequences" ID="ID_1663472381" CREATED="1318083208868" MODIFIED="1318083343867">
<node TEXT="restore the previous Sequence if needed" ID="ID_1271242717" CREATED="1318083216138" MODIFIED="1318083226258">
<node TEXT="the data will be all up to date" ID="ID_943982727" CREATED="1318083236745" MODIFIED="1318083246075">
<node TEXT="Archive the Sequence folder only" ID="ID_1733888909" CREATED="1318083494311" MODIFIED="1318083517469">
<icon BUILTIN="idea"/>
<node TEXT="Murat will not follow this pattern" ID="ID_1810558772" CREATED="1318083518645" MODIFIED="1318083526282">
<node TEXT="he will try to archive&#xa;the whole project folder" ID="ID_326851130" CREATED="1318083527392" MODIFIED="1318083557248"/>
</node>
</node>
</node>
</node>
</node>
</node>
</node>
<node TEXT="archive all the project folder and&#xa;exclude the other Sequences" ID="ID_1515770800" CREATED="1318083356166" MODIFIED="1318083380016">
<node TEXT="it is a big problem" ID="ID_1856241629" CREATED="1318083381107" MODIFIED="1318085134243" COLOR="#ff0000">
<font NAME="Liberation Sans" SIZE="12"/>
<icon BUILTIN="yes"/>
<node TEXT="cause there will be two metadat.db&#xa;files, one in archive and one in&#xa;fileserver" ID="ID_48410293" CREATED="1318083387397" MODIFIED="1318083407555">
<node TEXT="in any case this will create a big problem" ID="ID_1151632395" CREATED="1318083408380" MODIFIED="1318083428025">
<node TEXT="Don&apos;t archive the metadata.db&#xa;if you need to archive only one&#xa;Sequence" ID="ID_221490723" CREATED="1318083431385" MODIFIED="1318085161881" COLOR="#990000">
<font NAME="Liberation Sans" SIZE="12" BOLD="false"/>
<icon BUILTIN="idea"/>
<node TEXT="how will you find the metadata.db if&#xa;you not archive the whole project" ID="ID_1656074354" CREATED="1318083638468" MODIFIED="1318085144620" COLOR="#ff0000">
<font NAME="Liberation Sans" SIZE="12"/>
<icon BUILTIN="yes"/>
</node>
</node>
</node>
</node>
</node>
</node>
</node>
<node TEXT="when restored an old sequence&#xa;what will happen to the metada.db file" ID="ID_795141182" CREATED="1318082307215" MODIFIED="1318082350707">
<node TEXT="can be skipped if there is a&#xa;metadata.db file" ID="ID_1466295673" CREATED="1318082332061" MODIFIED="1318082455831">
<node TEXT="the file should have the latest information" ID="ID_1221826606" CREATED="1318082354900" MODIFIED="1318082365317"/>
<node TEXT="merging is a headache if the&#xa;sequences created and&#xa;archived separately" ID="ID_179690209" CREATED="1318082370569" MODIFIED="1318082466252"/>
<node TEXT="does it mean the file has all the information" ID="ID_616518794" CREATED="1318082986299" MODIFIED="1318082996827">
<node TEXT="no" ID="ID_1578345699" CREATED="1318083067745" MODIFIED="1318083068982"/>
</node>
</node>
</node>
<node TEXT="keep the projects until they&#xa;are really not needed" ID="ID_187980372" CREATED="1318083826561" MODIFIED="1318083849943">
<font NAME="Aharoni" SIZE="12"/>
<icon BUILTIN="idea"/>
<node TEXT="keep a live backup on hdd" ID="ID_1540190642" CREATED="1318083858812" MODIFIED="1318083891994"/>
<node TEXT="it will consume space&#xa;in the server" ID="ID_1023721241" CREATED="1318083869149" MODIFIED="1318083885352"/>
</node>
<node TEXT="Do it as you do before" ID="ID_479552916" CREATED="1318083899795" MODIFIED="1318083914388">
<icon BUILTIN="idea"/>
<node TEXT="Archive the projects when&#xa;the project is finished" ID="ID_493309494" CREATED="1318083917236" MODIFIED="1318083999353">
<node TEXT="open up a new project with&#xa;a new descriptive name" ID="ID_1741365438" CREATED="1318083954713" MODIFIED="1318084093731">
<node TEXT="For Example:&#xa;MIGROS_2011&#xa;MIGROS_2012" ID="ID_942126565" CREATED="1318084095188" MODIFIED="1318084104305"/>
<node TEXT="avoid having two sequences&#xa;for the same project when there&#xa;is to much time difference&#xa;between the Sequences" ID="ID_508971868" CREATED="1318083957042" MODIFIED="1318084029112"/>
</node>
</node>
</node>
</node>
<node TEXT="Asset" POSITION="left" ID="ID_378281366" CREATED="1318082059170" MODIFIED="1318082088700"/>
<node TEXT="Place the metadata.db&#xa;under the sequence root" POSITION="right" ID="ID_1948138898" CREATED="1318082805343" MODIFIED="1318082850704">
<font NAME="Aharoni" SIZE="12"/>
<icon BUILTIN="help"/>
<node TEXT="it is a big problem to manage the&#xa;Project class if there is two Sequences" ID="ID_298894725" CREATED="1318082531111" MODIFIED="1318082937622">
<node TEXT="don&apos;t map the Project class" ID="ID_1947425786" CREATED="1318082863081" MODIFIED="1318082875499">
<node TEXT="it will be hard to recreate it&#xa;when needed,&#xa;from the Sequences table" ID="ID_95017697" CREATED="1318082877154" MODIFIED="1318082900468">
<node TEXT="it is awkward to&#xa;not to place it in a&#xa;Table but use it" ID="ID_1608051593" CREATED="1318082902194" MODIFIED="1318082924122"/>
</node>
</node>
<node TEXT="two sequences are refering the&#xa;same object in different databases&#xa;not very usual" ID="ID_538015180" CREATED="1318082939027" MODIFIED="1318082962921"/>
</node>
</node>
<node TEXT="AssetType" POSITION="left" ID="ID_511310110" CREATED="1318082071388" MODIFIED="1318082075910"/>
<node TEXT="Sequence" POSITION="left" ID="ID_1614137048" CREATED="1318082066199" MODIFIED="1318082091741">
<node TEXT="managed by SQLAlchemy" ID="ID_1850280339" CREATED="1318082094914" MODIFIED="1318082126209">
<node TEXT="metadata.db file placed under&#xa;the sequence root" ID="ID_375432059" CREATED="1318082518232" MODIFIED="1318082530124"/>
</node>
</node>
<node TEXT="Project" POSITION="left" ID="ID_1071731704" CREATED="1318082051240" MODIFIED="1318082055446"/>
<node TEXT="Shot" POSITION="left" ID="ID_16509818" CREATED="1318082077008" MODIFIED="1318082078373"/>
<node TEXT="a central&#xa;metadata storage" POSITION="right" ID="ID_374614094" CREATED="1318082639185" MODIFIED="1318082649312">
<node TEXT="then it is Stalker or&#xa;it will step on Stalkers feet" ID="ID_1372723796" CREATED="1318082650528" MODIFIED="1318082668985">
<node TEXT="and it will be hard to update&#xa;the db if it is not a db server" ID="ID_24552489" CREATED="1318083759536" MODIFIED="1318083790361"/>
</node>
</node>
</node>
</map>
