from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from xml.sax.saxutils import escape
from xml.etree import ElementTree as E
from PIL import Image
import re,json,hashlib,copy
ROOT=Path.cwd();OUT=ROOT/'outputs/reports/template_aligned';OUT.mkdir(parents=True,exist_ok=True)
source=ROOT/'outputs/reports/final_report_en/final_report_en.docx'
plan=json.loads((ROOT/'outputs/reports/final_report_en/report_payload.json').read_text(encoding='utf-8'))
blocks=copy.deepcopy(plan['blocks'])
# Use only existing notebook figures. Do not draw, regenerate, crop or alter artwork.
images={
'class_distance':('outputs/figures/eda05_late_rate_by_distance_group.png','Late-delivery rate by distance group. Rates are descriptive and use valid delivery labels.'),
'labels':('outputs/figures/eda01_late_distribution.png','Late and Not Late counts in the labelled sample.'),
'monthly':('outputs/figures/eda03_late_rate_by_month.png','Observed late rates by purchase month. The original EDA plot excludes months with fewer than 100 valid labels; it does not display confidence intervals.'),
'adjusted_or':('outputs/figures/regression/adjusted_or_key_contrasts.png','Adjusted delivery odds ratios and calendar sensitivity. Seven-day clustered intervals are pointwise 95%.'),
'validation_models':('outputs/figures/ml_catboost/20261111_152855_922857/validation_a_pr_curve.png','Precision-recall curves for five baseline models on Validation A.'),
'sampling':('outputs/figures/ml_random_oversampling/20261111_160816_219035/validation_a_pr_curve.png','Validation A precision-recall curves after random oversampling in Train only.'),
'undersampling':('outputs/figures/ml_random_undersampling/20261111_161215_292137/validation_a_pr_curve.png','Validation A precision-recall curves after random undersampling in Train only.'),
'calibration_transfer':('outputs/figures/ml_calibration/20261111_154951_108593/calibration_and_threshold.png','Sigmoid calibration and threshold selection on Validation B. Both panels use fitting/selection data, not an independent test sample.'),
'test_confusion':('outputs/figures/ml_test/20261111_160038_411032/final_test_results.png','Saved Test results: raw precision-recall curves, CatBoost calibration and confusion matrix at the frozen threshold.')}
new=[];skip=False
for b in blocks:
 if b['type']=='heading' and b['text']=='Contents':skip=True;continue
 if skip is True:
  if b['type']=='heading' and b['text'].startswith('1. '):skip=False
  else:continue
 if b['type']=='figure':
  if b['key'] in ['framework','review_cancellation']:continue
  key=b['key'];path,caption=images[key];b['path']=str((ROOT/path).resolve());b['caption']=caption
  if key=='class_distance':
   pp,cc=images['labels'];new.append(dict(type='figure',key='labels',path=str((ROOT/pp).resolve()),caption=cc))
  new.append(b)
  if key=='sampling':
   pp,cc=images['undersampling'];new.append(dict(type='figure',key='undersampling',path=str((ROOT/pp).resolve()),caption=cc))
  continue
 if b['type']=='paragraph':
  b['text']=b['text'].replace('Monthly plots include pointwise Wilson 95% intervals and mark small groups.','The monthly summary includes Wilson 95% intervals; the original monthly EDA figure selected for this report shows observed rates and excludes small groups.').replace('Stage 3 and Stage 4 also use different samples and estimands','Stage 3 and Stage 4 also use different samples and quantities being estimated')
 if b['type']=='heading' and b['text']=='2.2 Research Gap and Contribution':
  new.extend([
   dict(type='heading',text='2.2 Theoretical Background',level=2),
   dict(type='paragraph',text='Descriptive analysis shows what happened in the observed sample. A hypothesis test asks whether a selected difference is compatible with a null model. Multivariable logistic regression estimates an association while holding included variables fixed. Prediction asks how well the fitted rule works on later orders. These tasks use different evidence, so a small p-value does not establish a useful predictor or a causal effect.'),
   dict(type='paragraph',text='A logistic odds ratio compares odds, not probabilities. For prediction, Average Precision focuses on ranking the minority Late class. ROC-AUC measures ranking across the two classes, while Brier and LogLoss assess the reported probabilities. Calibration changes the meaning of a risk score; threshold selection converts that score into an action. A time split makes the evaluation closer to predicting later orders, although it does not remove every source of leakage or population change.'),
   dict(type='heading',text='2.3 Research Gap',level=2),
   dict(type='paragraph',text='The gap is defined from the selected studies and the practical problem, not from a claim that no earlier work exists. The review in [1] identifies a need to connect predictive performance with practical use and suitable prediction timing. The Olist abstract [2] brings prediction, thresholds and explanation together. These sources show that the topic is already studied. This project examines the following narrower questions in one shared order-level workflow.'),
   dict(type='heading',text='2.3.1 Purchase-Time Information and Later-Period Evaluation',level=3),
   dict(type='paragraph',text='An accurate historical model may use information that was not available when the purchase was made. This project therefore states a purchase-time decision point, removes post-delivery predictors and uses chronological samples with label-availability rules. However, the time when some prices, seller information and weather observations became available remains uncertain. The contribution is a clearer audit of these assumptions, not a claim that early-prediction leakage has been fully solved.'),
   dict(type='heading',text='2.3.2 Unadjusted Patterns, Adjusted Associations and Prediction',level=3),
   dict(type='paragraph',text='Simple comparisons can mix distance, location, order composition and time. A factor may be different between Late and Not Late orders but become uncertain after adjustment. It may also remain statistically associated without improving prediction. The backorder study [3] has a different target, so its scores cannot answer these Olist questions. The project links four selected tests to adjusted delivery models and separate temporal ML results. Reviews and cancellation provide descriptive context only.'),
   dict(type='heading',text='2.3.3 Added Value of External and Product Features',level=3),
   dict(type='paragraph',text='Including holidays or weather in a model does not show that they add useful information. That question requires controlled comparisons with the same algorithm, records and preprocessing. The project defines basic, price/product, holiday and weather groups and prepares suitable order-level inputs. However, the required add/remove-group experiment has not been completed. Question D remains open; the report does not claim to close this gap or show that external data improve performance.'),
   dict(type='heading',text='2.3.4 Reliable Probabilities and Operational Workload',level=3),
   dict(type='paragraph',text='A risk ranking is useful only when its probability scale and action rule fit the setting. The Olist abstract [2] highlights threshold calibration, while this project additionally examines whether a B-fitted correction transfers to a later Test period. It reports Brier, LogLoss, precision, recall, F1 and the proportion of orders alerted. This separates statistical performance from staff workload. The observed transfer failure is a result to explain, rather than a reason to retune on the same Test. No business benefit or intervention effect has been measured.'),
   dict(type='heading',text='2.4 Research Position and Evidence Boundaries',level=2),
   dict(type='paragraph',text='The study offers a transparent comparison and an account of where the current evidence is weak. It does not propose a new algorithm, establish causal effects or demonstrate deployment readiness. Its strongest contribution is the joint reporting of data assumptions, descriptive results, adjusted delivery associations and temporal probability/threshold behaviour. Independent confirmation and the feature-group experiment remain future work.'),
   dict(type='table',key='gap',caption='Research gaps, project responses and completion status',headers=['Gap','Project response','Evidence / status'],rows=[['Purchase-time information','Audit predictors; temporal splits and label cutoffs','Implemented; some source availability remains unverified'],['Association versus prediction','Four tests, adjusted delivery regression and separate ML evaluation','Implemented; exploratory and observational'],['Added feature-group value','Define basic, product/price, holiday and weather groups','Inputs prepared; ablation not run'],['Probability and workload transfer','Calibrate on B; freeze threshold; evaluate later Test','Implemented; transfer is weak and alert burden is high']])
  ])
  skip='old_gap'
  continue
 if skip=='old_gap' and b['type']=='paragraph':skip=False;continue
 new.append(b)
# The loop above skips only the obsolete contribution paragraph; ensure later chapters survive.
assert any(b.get('text','').startswith('8. Conclusion') for b in new)
blocks=new
(OUT/'report_blocks.json').write_text(json.dumps(blocks,ensure_ascii=False,indent=2),encoding='utf-8')
manifest=[]
for b in blocks:
 if b['type']=='figure':
  p=Path(b['path']);assert p.is_file() and p.resolve().is_relative_to((ROOT/'outputs/figures').resolve())
  manifest.append(dict(key=b['key'],path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),caption=b['caption']))
(OUT/'image_sources.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Prepared content:',len(blocks),'blocks;',len(manifest),'unchanged original images')
# Build an editable Word master with live fields, captions, bookmarks and references.
with ZipFile(source) as z:files={name:z.read(name) for name in z.namelist()}
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';NS={'w':W}
raw=files['word/document.xml'].decode('utf-8')
cover_tables=list(re.finditer(r'<w:tbl(?:\s[^>]*)?>.*?</w:tbl>',raw,re.S))[:2];assert len(cover_tables)==2
prefix=raw[:cover_tables[-1].end()]
sections=list(re.finditer(r'<w:sectPr(?:\s[^>]*)?>.*?</w:sectPr>',raw,re.S));sect=sections[-1].group()
# Keep the source logo and cover tables; acknowledgement is not copied or written.
def run(t,bold=False,italic=False,size=None,hidden=False):
 props='<w:rPr>'+('<w:b/>' if bold else '')+('<w:i/>' if italic else '')+(f'<w:sz w:val="{size}"/>' if size else '')+('<w:vanish/>' if hidden else '')+'</w:rPr>'
 return '<w:r>'+props+'<w:t xml:space="preserve">'+escape(str(t))+'</w:t></w:r>'
def field(code,result='1',hidden=False):
 rp='<w:rPr><w:vanish/></w:rPr>' if hidden else ''
 if code.startswith('TC '):return ''
 if False:return '<w:r>'+rp+'<w:fldChar w:fldCharType="begin"/></w:r><w:r>'+rp+'<w:instrText xml:space="preserve"> '+escape(code)+' </w:instrText></w:r><w:r>'+rp+'<w:fldChar w:fldCharType="end"/></w:r>'
 return '<w:r>'+rp+'<w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r><w:r>'+rp+'<w:instrText xml:space="preserve"> '+escape(code)+' </w:instrText></w:r><w:r>'+rp+'<w:fldChar w:fldCharType="separate"/></w:r>'+run(result,hidden=hidden)+'<w:r>'+rp+'<w:fldChar w:fldCharType="end"/></w:r>'
def para(content='',style='Normal',before=False,keep=False,center=False,number=None):
 props=f'<w:pStyle w:val="{style}"/>'+('<w:pageBreakBefore/>' if before else '')+('<w:keepNext/>' if keep else '')+('<w:jc w:val="center"/>' if center else '')
 if number is not None:props+=f'<w:numPr><w:ilvl w:val="{number}"/><w:numId w:val="{num_id}"/></w:numPr>'
 return '<w:p><w:pPr>'+props+'</w:pPr>'+content+'</w:p>'
# Add a single multilevel list for chapter and subsection numbering.
nraw=files['word/numbering.xml'].decode('utf-8');nr=E.fromstring(nraw)
abstract_id=max([int(x.attrib['{'+W+'}abstractNumId']) for x in nr.findall('w:abstractNum',NS)]+[0])+1
num_id=max([int(x.attrib['{'+W+'}numId']) for x in nr.findall('w:num',NS)]+[0])+1
levels=''
for level,label in [(0,'CHAPTER %1:'),(1,'%1.%2.'),(2,'%1.%2.%3.')]:
 levels+=f'<w:lvl w:ilvl="{level}"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="{label}"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="0" w:hanging="0"/></w:pPr></w:lvl>'
numxml=f'<w:abstractNum w:abstractNumId="{abstract_id}"><w:multiLevelType w:val="multilevel"/>{levels}</w:abstractNum><w:num w:numId="{num_id}"><w:abstractNumId w:val="{abstract_id}"/></w:num>'
files['word/numbering.xml']=('<w:numbering xmlns:w="'+W+'">'+numxml+'</w:numbering>').encode('utf-8')
styles=files['word/styles.xml'].decode('utf-8')
for sid,name,size,outline in [('Normal','Normal',24,None),('Heading1','heading 1',28,0),('Heading2','heading 2',26,1),('Heading3','heading 3',24,2),('FrontHeading','Front matter title',28,None),('FrontEntry','Front matter entry',28,None),('Caption','Caption',22,None),('ImageSource','Image source',18,None)]:
 style=f'<w:style w:type="paragraph" w:styleId="{sid}"><w:name w:val="{name}"/><w:basedOn w:val="Normal"/>' if sid!='Normal' else '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/>'
 pp='<w:spacing w:after="120" w:line="276" w:lineRule="auto"/>'
 if sid.startswith('Heading') or sid in ['FrontHeading','FrontEntry']:pp+='<w:keepNext/><w:keepLines/><w:spacing w:before="180" w:after="180"/>'
 if sid in ['Heading1','FrontHeading','FrontEntry']:pp+='<w:pageBreakBefore/>'
 if outline is not None:pp+=f'<w:outlineLvl w:val="{outline}"/>'
 if sid=='Caption':pp+='<w:keepNext/>'
 style+='<w:pPr>'+pp+'</w:pPr><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:color w:val="000000"/><w:sz w:val="'+str(size)+'"/>'+('<w:b/>' if sid.startswith('Heading') or sid in ['FrontHeading','FrontEntry','Caption'] else '')+'</w:rPr></w:style>'
 pattern=rf'<w:style\b(?=[^>]*w:styleId="{sid}")[^>]*>.*?</w:style>'
 if re.search(pattern,styles,re.S):styles=re.sub(pattern,lambda m:style,styles,flags=re.S)
 else:styles=styles.replace('</w:styles>',style+'</w:styles>')
files['word/styles.xml']=styles.encode('utf-8')
settings=files['word/settings.xml'].decode('utf-8');settings=re.sub(r'<w:updateFields\b[^>]*/>','',settings);settings=settings.replace('</w:settings>','<w:updateFields w:val="true"/></w:settings>');files['word/settings.xml']=settings.encode()
# Abbreviation entries are TC fields in the text; the list is a live TOC field filtered by A.
abbreviations={'AP':'Average Precision','AUC':'Area Under the Curve','BRL':'Brazilian real','CI':'Confidence Interval','EDA':'Exploratory Data Analysis','F1':'Harmonic mean of precision and recall','FP':'False Positive','FN':'False Negative','INMET':'Instituto Nacional de Meteorologia','ML':'Machine Learning','OR':'Odds Ratio','PR':'Precision-Recall','ROC':'Receiver Operating Characteristic','RQ':'Research Question','TN':'True Negative','TP':'True Positive','UTC':'Coordinated Universal Time','VIF':'Variance Inflation Factor'}
seen=set();bookmark_id=300

def plain(t):
 global bookmark_id
 parts=[];last=0
 pattern=r'(?<![A-Za-z0-9_])('+ '|'.join(sorted(abbreviations,key=len,reverse=True))+r')(?![A-Za-z0-9_])'
 for m in re.finditer(pattern,t):
  parts.append(run(t[last:m.start()]));term=m.group()
  if term not in seen:
   bookmark_id+=1;parts.append(f'<w:bookmarkStart w:id="{bookmark_id}" w:name="_Abbr_{term}"/>'+run(term)+f'<w:bookmarkEnd w:id="{bookmark_id}"/>');seen.add(term)
  else:parts.append(run(term))
  last=m.end()
 parts.append(run(t[last:]));return ''.join(parts)
# Front lists are real Word fields; Word automation updates their cached text before delivery.
content=[]
for title,code in [('TABLE OF CONTENTS','TOC \\o "1-3" \\h \\z \\u \\t "Front matter entry,1"'),('LIST OF ABBREVIATIONS','TOC \\f A \\h \\z'),('LIST OF FIGURES','TOC \\h \\z \\c "Figure"'),('LIST OF TABLES','TOC \\h \\z \\c "Table"')]:
 content.append(para(run(title),style='FrontHeading' if title=='TABLE OF CONTENTS' else 'FrontEntry',before=True))
 if title!='TABLE OF CONTENTS':content.append(para(field('TC "'+title+'" \\f C \\l 1','',hidden=True)))
 content.append('[[ABBREVIATIONS_TABLE]]' if title=='LIST OF ABBREVIATIONS' else para(field(code,'Update fields to display this list.')))
# Tables have repeated headers and cannot split individual rows across pages.
def abbreviation_fields(value):
 global bookmark_id
 result=''
 for term in re.findall(r'(?<![A-Za-z0-9_])(?:'+ '|'.join(abbreviations)+r')(?![A-Za-z0-9_])',str(value)):
  if term not in seen:
   bookmark_id+=1;result+=f'<w:bookmarkStart w:id="{bookmark_id}" w:name="_Abbr_{term}"/><w:bookmarkEnd w:id="{bookmark_id}"/>';seen.add(term)
 return result

def xml_table(headers,rows):
 cols=len(headers);widths={2:[2200,6800],3:[2000,3500,3500],4:[2200,3000,1800,2000],5:[2400,1300,1500,2000,1800],6:[750,1000,1950,2250,1500,1550]}[cols]
 result='<w:tbl><w:tblPr><w:tblW w:w="9000" w:type="dxa"/><w:tblLayout w:type="fixed"/><w:tblBorders>'+''.join(f'<w:{side} w:val="single" w:sz="4" w:color="7F7F7F"/>' for side in ['top','left','bottom','right','insideH','insideV'])+'</w:tblBorders><w:tblCellMar><w:top w:w="70" w:type="dxa"/><w:left w:w="70" w:type="dxa"/><w:bottom w:w="70" w:type="dxa"/><w:right w:w="70" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>'+''.join(f'<w:gridCol w:w="{v}"/>' for v in widths)+'</w:tblGrid>'
 for i,row in enumerate([headers]+rows):
  result+='<w:tr><w:trPr><w:cantSplit/>'+('<w:tblHeader/>' if i==0 else '')+'</w:trPr>'
  for j,value in enumerate(row):
   result+=f'<w:tc><w:tcPr><w:tcW w:w="{widths[j]}" w:type="dxa"/>'+('<w:shd w:fill="E7EEEE"/>' if i==0 else '')+'</w:tcPr><w:p><w:pPr><w:spacing w:after="40" w:line="240" w:lineRule="auto"/></w:pPr>'+run(str(value),bold=i==0,size=20 if cols<6 else 18)+abbreviation_fields(value)+'</w:p></w:tc>'
  result+='</w:tr>'
 return result+'</w:tbl>'
rels=files['word/_rels/document.xml.rels'].decode('utf-8');existing_ids=re.findall(r'Id="rId(\d+)"',rels);rid=max(map(int,existing_ids or ['0']))+1
media_index=200;chapter=0;counts={'Table':{},'Figure':{}};caption_records=[];fig_records=[]
def caption(label,key,description):
 global bookmark_id
 n=counts[label].get(chapter,0)+1;counts[label][chapter]=n;number=f'{chapter}.{n}' if chapter else f'A.{n}';anchor='_'+label+'_'+key
 bookmark_id+=1
 numberxml=(field('STYLEREF 1 \\s',str(chapter))+run('.')+field('SEQ '+label+' \\* ARABIC \\s 1',str(n))) if chapter else (run('A.')+field('SEQ '+label+' \\* ARABIC'+(' \\r 1' if n==1 else ''),str(n)))
 cap=para(run(label+' ')+f'<w:bookmarkStart w:id="{bookmark_id}" w:name="{anchor}"/>'+numberxml+f'<w:bookmarkEnd w:id="{bookmark_id}"/>'+run('. '+description),style='Caption',keep=True)
 caption_records.append(dict(label=label,key=key,number=number,anchor=anchor,text=description));return cap,anchor,number

def picture(b):
 global rid,media_index
 path=Path(b['path']);assert path.resolve().is_relative_to((ROOT/'outputs/figures').resolve())
 data=path.read_bytes();name=f'report_source_{media_index}.png';files['word/media/'+name]=data
 rel=f'<Relationship Id="rId{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{name}"/>';relid='rId'+str(rid);rid+=1;media_index+=1
 global rels
 rels=rels.replace('</Relationships>',rel+'</Relationships>')
 with Image.open(path) as im:width,height=im.size
 wp=450;hp=wp*height/width
 if hp>340:wp*=340/hp;hp=340
 cx,cy=int(wp*12700),int(hp*12700)
 xml=f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{media_index}" name="{b["key"]}" descr="{escape(b["caption"],{chr(34):"&quot;"})}"/><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="0" name="{name}"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="{relid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>'
 fig_records.append(dict(key=b['key'],source=str(path.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),embedded='word/media/'+name))
 return para(xml,center=True,keep=True)

for b in blocks:
 typ=b['type']
 if typ=='heading':
  title=b['text'];level=b.get('level',1)
  if level==1 and re.match(r'^\d+\. ',title):
   chapter=int(title.split('.')[0]);title=re.sub(r'^\d+\. ','',title).upper();content.append(para(run(title),style='Heading1',before=True,number=0))
  elif level in [2,3]:
   title=re.sub(r'^\d+(?:\.\d+)+\s+','',title);content.append(para(run(title),style='Heading'+str(level),number=level-1))
  else:
   if title.startswith('Appendix'):chapter=0
   content.append(para(run(title.upper()),style='FrontEntry',before=True));content.append(para(field('TC "'+title+'" \\f C \\l 1','',hidden=True)))
 elif typ=='paragraph':content.append(para(plain(b['text'])))
 elif typ=='table':
  description=re.sub(r'^Table\s+[\dA]+\.\d+\.\s*','',b['caption'])
  cap,anchor,number=caption('Table',b['key'],description)
  content.append(para(run('Table ')+field('REF '+anchor+' \\h',number)+run(' summarises the following information.')))
  content.append(cap);content.append(xml_table(b['headers'],b['rows']));content.append(para())
 elif typ=='figure':
  cap,anchor,number=caption('Figure',b['key'],b['caption'])
  content.append(para(run('The corresponding results are shown in Figure ')+field('REF '+anchor+' \\h',number)+run('.')))
  content.append(picture(b));content.append(cap)
  content.append(para(run('Source: '+str(Path(b['path']).relative_to(ROOT)).replace('\\','/'),size=18),style='ImageSource'))
# Keep abbreviation definitions inspectable in a reproducibility manifest.
(OUT/'abbreviations.json').write_text(json.dumps({k:abbreviations[k] for k in sorted(seen)},indent=2),encoding='utf-8')
glossary_rows=[]
for i,term in enumerate(sorted(seen),1):glossary_rows.append([str(i),term,abbreviations[term],'@@PAGE_'+term+'@@'])
glossary=xml_table(['No.','Abbreviation','Full term','First-use page'],glossary_rows)
for term in sorted(seen):
 glossary=glossary.replace(run('@@PAGE_'+term+'@@',size=20),field('PAGEREF _Abbr_'+term+' \\h','1'))
files['word/document.xml']=(prefix+''.join(content).replace('[[ABBREVIATIONS_TABLE]]',glossary)+sect+'</w:body></w:document>').encode('utf-8')
files['word/_rels/document.xml.rels']=rels.encode('utf-8')
# New image names use the PNG content type already present in the source document.
assert b'Extension="png"' in files['[Content_Types].xml']
for name,data in files.items():
 if name.endswith('.xml') or name.endswith('.rels'):E.fromstring(data)
path=OUT/'final_report_en.docx'
with ZipFile(path,'w',ZIP_DEFLATED) as z:
 for name,data in files.items():z.writestr(name,data)
(OUT/'caption_manifest.json').write_text(json.dumps(caption_records,indent=2),encoding='utf-8')
(OUT/'image_sources.json').write_text(json.dumps(fig_records,indent=2),encoding='utf-8')
with ZipFile(path) as z:
 assert z.testzip() is None
 for record in fig_records:assert hashlib.sha256(z.read(record['embedded'])).hexdigest()==record['sha256']
print('Built Word master:',len(caption_records),'captions;',len(fig_records),'original images;',len(seen),'abbreviations')
