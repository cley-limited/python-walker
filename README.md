# Python walker
This is an early version of a recovered package to walk Python data structures, in particular `sys.modules`.

## Documentation.todo
- Give some kind of outline of what it is trying to do.
- Describe the walker:
	- order of the walk, occurs checks;
	- depth limits;
	- the visitor and the various payload data functions.
- Describe the module walker.
- What walker methods are and how to define them:
	- the implicit global list;
	- and its deficiencies.
- Module dependency graphs:
	- why they are not really well-defined;
- Module tools:
	- recursively finding modules;
	- sanity checking `sys.modules` in various ways.

## History
I (Tim Bradshaw) wrote the original version of this package as a tool to try and draw pictures of data structures in Python programs: by walking over the structures and emitting something which could be parsed by a graph-drawing tool such as [Graphviz](http://www.graphviz.org/)[^1].  In particular it was used to draw graphs of module dependencies.

The code now in `pythonwalker.mt` originated rather later and separately, as a sanity-checker for `sys.modules`[^2].

Everything has since been somewhat revamped for more recent Python versions: it probably won't work in anything older than 2.7.

## Copyright and license
Copyright &copy; 2004, 2008, 2015, Cley Limited.

Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

---
[^1]: Originally, in fact, this spat out Lisp sexps which were injested by [LispWorks](http://www.lispworks.com/) and drawn using its grapher.

[^2]: Why a sanity-checker for `sys.modules` is *needed* is a question I have wondered about: couldn't it just map module names to modules?  I think the answer is that, if it did that, it would be a many-to-one map, and naïve programs which walked over `sys.modules` would then walk each module multiple times.  That's not a good reason, but it's the only one I can think of to explain this idiocy.