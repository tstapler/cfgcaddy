require 'byebug'

Given(/a directory containing/) do |dir_tree|
  tree = FileTree.new()
  tree.parse(dir_tree)
  tree.create_files(parent_path: aruba.config.home_directory)
end

Then(/^the directory should contain$/) do |dir_tree|
  tree = FileTree.new()

  tree.parse(dir_tree)
  expect(tree.paths(parent_path: aruba.config.home_directory)).to all be_an_existing_file
end

Then (/^the directory should contain the links:$/) do |dir_tree|
  tree = FileTree.new()

  tree.parse(dir_tree)
  files = tree.paths(parent_path: aruba.config.home_directory)
  symlinks = files.map{|path| File.symlink?(path)}
  expect(symlinks).to all(be_truthy)
end
