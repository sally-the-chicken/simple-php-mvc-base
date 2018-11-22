<?php

class Base_View {
    
    protected $_vars = array();
    protected $_content;
    protected $_filepath    = 'view';
    protected $_extension   = 'html';
    protected $_layoutpath  = 'layout';
    protected $_layout      = 'default';
    
    protected $_title;
    protected $_metas = array();
    protected $_jses = array('head' => array(), 'foot' => array()); 
    protected $_csses = array();
    
    protected $_is_ajax = false;
    
    public function ajax(){
        $this->_is_ajax = true;
        return $this;
    }

    public function unajax(){
        $this->_is_ajax = false;
        return $this;
    }
    
    public function set_title($title){
        $this->_title = $title;
        return $this;
    }
    
    public function add_js($position, $js_path){
        $this->_jses[$position][] = $js_path;
        return $this;
    }
    
    public function add_css($css_path){
        $this->_csses[] = $css_path;
        return $this;
    }
    
    public function add_meta($meta){
        $this->_metas[] = $meta;
        return $this;
    }
    
    public function set_var($key, $value) {
        $this->_vars[$key] = $value;
        return $this;
    }
    
    public function unset_var($key){
        unset($this->_vars[$key]);
        return $this;
    }
    
    public function set_content($filename){
        $this->_content = $filename;
        return $this;
    }
    
    protected function _tag_metas(){
        return implode("\n",$this->_metas);
    }
    protected function _tag_js($position){
        if (empty($this->_jses[$position])){
            return '';
        }
        return '<script type="text/javascript" src="'.implode("\"></script>\n<script type=\"text/javascript\" src=\"",$this->_jses[$position]).'"></script>';
    }
    protected function _tag_css(){
        if (empty($this->_csses)){
            return '';
        }
        return '<link rel="stylesheet" href="'.implode("\">\n<link rel=\"stylesheet\" href=\"",$this->_csses).'">';
    }
    
    public function show(){

        if (!empty($this->_vars)){
            extract($this->_vars);
        }
        $complete_path = $this->_filepath.DIRECTORY_SEPARATOR.$this->_content.'.'.$this->_extension;
        $head_title   = $this->_title;
        $tags_meta    = $this->_tag_metas();
        $tags_css     = $this->_tag_css();
        $tags_js_head = $this->_tag_js('head');
        $tags_js_foot = $this->_tag_js('foot');
        
        ob_start();
        include $complete_path;
        $content = ob_get_clean();
        
        if ($this->_is_ajax){
            echo $content;
            exit;
        }
        
        require_once $this->_layoutpath.DIRECTORY_SEPARATOR.$this->_layout.'.'.$this->_extension;
        
    }
    
}