require 'aruba/cucumber'
require 'fileutils'
require 'byebug'

class FileTree
  def initialize
    @tree = Hash.new{ |h,k| h[k] = Hash.new(&h.default_proc) }  
  end

  def parse(lines)
    parents = []
    last_depth = 0
    last_name = ""
    lines.each_line do |line|
      line.scan(/(^\t*)(.*)/) do |level_tabs, name|
        if level_tabs.size > last_depth
          parents.push(last_name)
        elsif level_tabs.size < last_depth
          parents.pop()
        end

        if !parents.empty?
          @tree.dig(*parents)&.store(name, {})
        else
          @tree[name] = {}
        end

        last_name = name
        last_depth = level_tabs.size
      end
    end
  end

  def to_hash
    return @tree
  end

  def create_files(parent_path: "")
    get_paths(@tree).each do |path| 
      complete_path = File.join(parent_path, path)
      create_file(complete_path)
      puts "Path: #{complete_path}"
    end
  end

  def paths(parent_path: "")
    return get_paths(@tree).map {|path| File.join(parent_path, path) }
  end
end

def get_paths(tree, prefix: [])
  paths = []
  tree.each do |key, value|
    if value.empty?
      paths.push(File.join(*prefix, key))
    else
      paths = paths + get_paths(value, prefix: [*prefix, key])
    end
  end
    return paths
end

def create_file(path)
  dir = File.dirname(path)

  unless File.directory?(dir)
    FileUtils.mkdir_p(dir)
  end
  puts("Directory: #{dir}, Path: #{path}")
  File.new(path, 'w')
end
