<?php
/**
 * @author $Author: holman $
 */

$applicationFormat = array(
    '_root'=>'application',
    'application'=>array(
        'childs'=>array(
            'required'=>array('metadata'),
        ),
    ),
    'metadata'=>array(
        'childs'=>array(
            'required'=>array(
                'dc:title',
            ),
            'optional'=>array(
                'dc:identifier',
                'dc:creator', 'dc:description', 'dc:format',
                'ls:url', 'ls:crc', 'dc:rights', 'dc:subject',
                // extra
                'ls:filename', 'ls:filesize', 'ls:mtime',
            ),
        ),
        'namespaces'=>array(
            'dc'=>"http://purl.org/dc/elements/1.1/",
            'dcterms'=>"http://purl.org/dc/terms/",
            'xbmf'=>"http://www.streamonthefly.org/xbmf",
            'xsi'=>"http://www.w3.org/2001/XMLSchema-instance",
            'xml'=>"http://www.w3.org/XML/1998/namespace",
        ),
    ),
    'dc:identifier'=>array(
        'type'=>'Text',
        'auto'=>TRUE,
    ),
    'dc:title'=>array(
        'type'=>'Text',
        'attrs'=>array('implied'=>array('xml:lang')),
    ),
    'dc:creator'=>array(
        'type'=>'Text',
        'area'=>'Application',
        'attrs'=>array('implied'=>array('xml:lang')),
    ),
    'dc:description'=>array(
        'type'=>'Longtext',
        'area'=>'Application',
        'attrs'=>array('implied'=>array('xml:lang')),
    ),
    'dc:format'=>array(
        'type'=>'Text',
        'area'=>'Application',
        'attrs'=>array('implied'=>array('xml:lang')),
    ),
    'dc:rights'=>array(
        'type'=>'Text',
        'area'=>'Application',
        'attrs'=>array('implied'=>array('xml:lang')),
    ),
    'dc:subject'=>array(
        'type'=>'Text',
        'area'=>'Application',
        'attrs'=>array('implied'=>array('xml:lang')),
    ),
    'ls:url'=>array(
        'type'=>'Text',
        'attrs'=>array('implied'=>array('xml:lang')),
    ),
    'ls:crc'=>array(
        'type'=>'Text',
        'attrs'=>array('implied'=>array('xml:lang')),
    ),
    'ls:filename'=>array(
        'type'=>'Text',
        'attrs'=>array('implied'=>array('xml:lang')),
    ),
    'ls:filesize'=>array(
	'type'=>'Int',
	'attrs'=>array('implied'=>array('xml:lang')),
    ),
    'ls:mtime'=>array(
        'type'=>'Int',
        // 'regexp'=>'^\d{4}(-\d{2}(-\d{2}(T\d{2}:\d{2}(:\d{2}\.\d+)?(Z)|([\+\-]?\d{2}:\d{2}))?)?)?$',
    ),
);

?>