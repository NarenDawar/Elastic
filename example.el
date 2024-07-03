$ This is an example file with some basic demonstration
$ Must run the shell file prior to running a .el file

$ Simple calculator and list manipulation example

function oopify(prefix): prefix + "oop"

function join(elements, separator):
	let result = ""
	let len = length(elements)

	repeat i = 0 to len 
		let result = result + elements/i
		if i != len - 1  let result = result + separator
	end

	return result
end

function map(elements, func):
	let new_elements = []

	repeat i = 0 to length(elements)
		append(new_elements, func(elements/i))
	end

	return new_elements
end

print("Greetings universe!")

repeat i = 0 to 5
	print(join(map(["l", "sp"], oopify), ", "))
end

print(3 % 2)





