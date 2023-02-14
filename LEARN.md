# Learning how to manipulate Java's bytecode

<details>
    <summary>Table of Contents</summary>
    <ul>
        <li>
            <a href="#part-0-preface">Part 0: Preface</a>
            <ul>
                <li><a href="#credits">Credits</a></li>
                <li><a href="#prerequisites">Prerequisites</a></li>
                <li><a href="#concepts-covered">Concepts Covered</a></li>
            </ul>
        </li>
        <li><a href="#part-1-the-magic-of-a-classfile">Part 1. The magic of a classfile</a></li>
        <li><a href="#part-2-the-version-of-a-classfile">Part 2. The version of a classfile</a></li>
        <li><a href="#part-3-constant-pool">Part 3. Constant Pool</a></li>
        <li><a href="#part-4-reading-a-constant-pool">Part 4. Reading a constant pool</a></li>
        <li><a href="#part-5-coding-a-script-to-do-this">Part 5. Coding a script to do this</a></li>
        <li><a href="#part-6-beyond-the-constant-pool">Part 6. Beyond the constant pool</a></li>
        <li><a href="#part-7-the-practicality-of-this-knowledge">Part 7. The practicality of this knowledge</a></li>
    </ul>
</details>

## Part 0: Preface
### Credits
- [JVM Specifications](https://docs.oracle.com/javase/specs/jvms/se19/html/index.html)

### Prerequisites
- Basic understanding of hex/base-16 and binary
- Understanding of ASCII
- Basic knowledge of Java

### Concepts Covered
- Java Bytecode 
- Constant Pool

## Part 1. The magic of a classfile
According to [Wikipedia](https://en.wikipedia.org/wiki/Magic_number_(programming)#:~:text=A%20constant%20numerical%20or%20text%20value%20used%20to%20identify%20a%20file%20format%20or%20protocol%3B%20for%20files%2C%20see%20List%20of%20file%20signatures), a magic number is a constant numerical or text value used to identify a file format or protocol
This just means that every file starts with this value. For Java `.class` files (the files you get on compiling a `.java` file), this value is **`cafebabe`**
This means that the first four bytes of every `.class` file is `ca fe ba be` (a byte is two hex digits).
We can verify this by opening a `.class` file in a hex editor (or a program like `xxd`)

![Main.class](https://user-images.githubusercontent.com/105878671/218782209-7d7c69f6-d388-42bb-96b1-25a9c4fdf370.png)

Welcome our test subject, Main.class! All it does is print `Hello` to `stdout`.
We can clearly see, highlighted in baby blue, the `ca fe ba be`

## Part 2. The version of a classfile

The next four bytes, highlighted in red are the minor and major versions.
The major version to JRE version is given in the [JRE specs](https://docs.oracle.com/javase/specs/jvms/se19/html/jvms-4.html#jvms-4.1-200-B.2)
| Java SE |    Released    | Major | Supported majors |
|:-------:|:--------------:|:-----:|:----------------:|
| 1.0.2   | May 1996       | 45    | 45               |
| 1.1     | February 1997  | 45    | 45               |
| 1.2     | December 1998  | 46    | 45 .. 46         |
| 1.3     | May 2000       | 47    | 45 .. 47         |
| 1.4     | February 2002  | 48    | 45 .. 48         |
| 5.0     | September 2004 | 49    | 45 .. 49         |
| 6       | December 2006  | 50    | 45 .. 50         |
| 7       | July 2011      | 51    | 45 .. 51         |
| 8       | March 2014     | 52    | 45 .. 52         |
| 9       | September 2017 | 53    | 45 .. 53         |
| 10      | March 2018     | 54    | 45 .. 54         |
| 11      | September 2018 | 55    | 45 .. 55         |
| 12      | March 2019     | 56    | 45 .. 56         |
| 13      | September 2019 | 57    | 45 .. 57         |
| 14      | March 2020     | 58    | 45 .. 58         |
| 15      | September 2020 | 59    | 45 .. 59         |
| 16      | March 2021     | 60    | 45 .. 60         |
| 17      | September 2021 | 61    | 45 .. 61         |
| 18      | March 2022     | 62    | 45 .. 62         |
| 19      | September 2022 | 63    | 45 .. 63         |

## Part 3. Constant Pool

The next two bytes (in maroon) is the **constant pool count**.
Essentially all literals in Java are stored in a constant pool. Do a `int x = 5;`? 5 will end up somewhere in this pool. It includes names of functions, 
descriptors (like a compressed form of the signature), functions, classes, fields and interfaces used, other literals, [method handles](https://docs.oracle.com/javase/8/docs/api/java/lang/invoke/MethodHandle.html)
and a couple more kinds of elements.
The constant pool is the `count derived earlier - 1` elements long, and **all indices start from 1 not 0**

Each element starts with a single byte long tag, which denotes the type of element, followed by data as per the type of element. A table of CONSTANTs is given below.

|        Constant Kind        | Tag | Class File Version | Java SE | Description                                                                                                                                                                                                                                                                                                                                   | Length (w/o tag)            | Field 1                                                                        | Field 2                                                                                        |
|:---------------------------:|:---:|:------------------:|:-------:|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------|--------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| CONSTANT_Utf8               | 1   | 45.3               | 1.0.2   | It stores raw ASCII string                                                                                                                                                                                                                                                                                                                    | 2 + Length of string stored | The length (2 bytes) of the string                                             | The array of ASCII bytes storing the string                                                    |
| CONSTANT_Integer            | 3   | 45.3               | 1.0.2   | It stores a 4 byte long integer literal                                                                                                                                                                                                                                                                                                       | 4                           | The integer stored                                                             | -                                                                                              |
| CONSTANT_Float              | 4   | 45.3               | 1.0.2   | It stores a 4 byte long floating-point literal as per [IEEE 454](https://en.wikipedia.org/wiki/IEEE_754) standards                                                                                                                                                                                                                            | 4                           | The float stored                                                               | -                                                                                              |
| CONSTANT_Long               | 5   | 45.3               | 1.0.2   | It stores a 8 byte long integer literal                                                                                                                                                                                                                                                                                                       | 8                           | The high 4 bytes of long stored                                                | The low 4 bytes of the long stored                                                             |
| CONSTANT_Double             | 6   | 45.3               | 1.0.2   | It stores a 8 byte long floating-point literal as per [IEEE 454](https://en.wikipedia.org/wiki/IEEE_754) standards                                                                                                                                                                                                                            | 8                           | The high 4 bytes of double stored                                              | The low 4 bytes of the double stored                                                           |
| CONSTANT_Class              | 7   | 45.3               | 1.0.2   | It is used to represent a class/interface                                                                                                                                                                                                                                                                                                     | 2                           | The index into the constant pool of the `CONSTANT_Utf8` storing the name       | -                                                                                              |
| CONSTANT_String             | 8   | 45.3               | 1.0.2   | It stores a string literal                                                                                                                                                                                                                                                                                                                    | 2                           | The index into the constant pool of the `CONSTANT_Utf8` storing the string     | -                                                                                              |
| CONSTANT_Fieldref           | 9   | 45.3               | 1.0.2   | It represents a field on a class                                                                                                                                                                                                                                                                                                              | 4                           | The index into the constant pool of the `CONSTANT_Class` storing the class     | The index into the constant pool of the `CONSTANT_NameAndType` storing the name and descriptor |
| CONSTANT_Methodref          | 10  | 45.3               | 1.0.2   | It represents a method on a class                                                                                                                                                                                                                                                                                                             | 4                           | The index into the constant pool of the `CONSTANT_Class` storing the class     | The index into the constant pool of the `CONSTANT_NameAndType` storing the name and descriptor |
| CONSTANT_InterfaceMethodref | 11  | 45.3               | 1.0.2   | It represents an interface method on a class                                                                                                                                                                                                                                                                                                  | 4                           | The index into the constant pool of the `CONSTANT_Class` storing the class     | The index into the constant pool of the `CONSTANT_NameAndType` storing the name and descriptor |
| CONSTANT_NameAndType        | 12  | 45.3               | 1.0.2   | It is used to store the name and descriptor (condensed signature) of a CONSTANT_ref                                                                                                                                                                                                                                                           | 4                           | The index into the constant pool of the `CONSTANT_Utf8` storing the name       | The index into the constant pool of the `CONSTANT_Utf8` storing the descriptor                 |
| CONSTANT_MethodHandle       | 15  | 51.0               | 7       | It is used to store a method handle                                                                                                                                                                                                                                                                                                           | 3                           | A single byte from 1-9 denoting the kind of method handle                      | The index into the constant pool of the `CONSTANT_Utf8` storing the descriptor                 |
| CONSTANT_MethodType         | 16  | 51.0               | 7       | It is used to store a method type                                                                                                                                                                                                                                                                                                             | 2                           | The index into the constant pool of the `CONSTANT_Utf8` storing the descriptor | -                                                                                              |
| CONSTANT_Dynamic            | 17  | 55.0               | 11      | **COMPLEX WARNING** It is used to represent a dynamically-computed constant, an arbitrary value that is produced by invocation of a bootstrap method in the course of an `ldc` instruction, among others.  The auxiliary type specified by the structure constrains the type of the dynamically-computed constant                             | 4                           | The index into the **bootstrap methods** array storing the bootstrap method    | The index into the constant pool of the `CONSTANT_NameAndType` storing the name and descriptor |
| CONSTANT_InvokeDynamic      | 18  | 51.0               | 7       | **COMPLEX WARNING** It is used to represent a dynamically-computed call site, an instance of `java.lang.invoke.CallSite` that is produced by invocation of a bootstrap method in the course of an invokedynamic instruction.  The auxiliary type specified by the structure constrains the method type of the dynamically-computed call site. | 4                           | The index into the **bootstrap methods** array storing the bootstrap method    | The index into the constant pool of the `CONSTANT_NameAndType` storing the name and descriptor |
| CONSTANT_Module             | 19  | 53.0               | 9       | It is used to represent a [module](https://www.oracle.com/corporate/features/understanding-java-9-modules.html)                                                                                                                                                                                                                               | 2                           | The index into the constant pool of the `CONSTANT_Utf8` storing the name       | -                                                                                              |
| CONSTANT_Package            | 20  | 53.0               | 9       | It is used to represent a package exported/used                                                                                                                                                                                                                                                                                               | 2                           | The index into the constant pool of the `CONSTANT_Utf8` storing the name       | -                                                                                              |

Before we continue, I need to explain what a descriptor is. I kept referring to it as a condensed signature, and that is what it is!
Let's take a function `String func(int a, boolean[][] b)`. It has a return type of `java.lang.String` and takes two arguments (an integer and boolean).
A descriptor is in the format `(list of arguments separated by nothing)return type`
Each type used here is converted to an internal type as follows

> **Source**: [JVM Specifications Table 4.3-A](https://docs.oracle.com/javase/specs/jvms/se19/html/jvms-4.html#jvms-4.3.2-200)
> | Term           |   Type  |                                   Interpretation                                  |
> |:--------------:|:-------:|:---------------------------------------------------------------------------------:|
> | B              | byte    | signed byte                                                                       |
> | C              | char    | Unicode character code point in the Basic Multilingual Plane, encoded with UTF-16 |
> | D              | double  | double-precision floating-point value                                             |
> | F              | float   | single-precision floating-point value                                             |
> | I              | int     | integer                                                                           |
> | J              | long    | long integer                                                                      |
> | L ClassName ;  | object  | an instance of class ClassName                                                    |
> | S              | short   | signed short                                                                      |
> | Z              | boolean | true or false                                                                     |
> | V              | void    | **Only for return type** void return type 
> | [              | array   | one array dimension                                                               |

So the function would get converted to `(I[[Z)Ljava/lang/String;` (note the two `[`s for two dimensional array)
**The dot separator in all identifiers gets replaced with /**

You now have the necessary knowledge to read the constant pool

## Part 4: Reading a constant pool
Breaking a constant pool up is really easy if you do it mentally or with code. It isn't really a complex structure... until you have to deal with one element indexing some other element indexing some other element to finally get the name of a method used.

But leaving that aside let's get back to `Main.class`

![Main.class](https://user-images.githubusercontent.com/105878671/218782209-7d7c69f6-d388-42bb-96b1-25a9c4fdf370.png)

If you look past the `00 1d`, you can see that I've added boxes. As you might have guessed, these are the constant pool elements. 

And yes, I added these. By hand. _Save my sanity please._

You can see `0x1d - 1` or 28 elements. Try looking through every index and figuring out what the element based on the first byte (the tag)

## Part 5: Coding a script to do this
This is why you probably came to this file, to see how to replicate this for yourself.

But for your own good, I'm going to let you down.

I don't want you to spoonfeed you the answer because it's much harder to learn then.

I've given you the resources, code away, and I promise you you'll be more satisfied than if I just dumped it in a Gist.

(frankly speaking, the code isn't that complicated either, if you find it tough, I wouldn't learn a Java classfile structure anytime soon)

## Part 6: Beyond the constant pool
You might have noticed that beyond the highlighted constant pool is more hex data.
This is the rest of the `Main` class.
In brief, the next 2 bytes are the access flags of the class, ORed together into a single number

> **Source**: [JVM Specifications Table 4.1-B](https://docs.oracle.com/javase/specs/jvms/se19/html/jvms-4.html#jvms-4.1-200-E.1)
>
> |    Flag Name   |  Value |                                   Interpretation                                  |
> |:--------------:|:------:|:---------------------------------------------------------------------------------:|
> | ACC_PUBLIC     | 0x0001 | Declared public; may be accessed from outside its package.                        |
> | ACC_FINAL      | 0x0010 | Declared final; no subclasses allowed.                                            |
> | ACC_SUPER      | 0x0020 | Treat superclass methods specially when invoked by the invokespecial instruction. |
> | ACC_INTERFACE  | 0x0200 | Is an interface, not a class.                                                     |
> | ACC_ABSTRACT   | 0x0400 | Declared abstract; must not be instantiated.                                      |
> | ACC_SYNTHETIC  | 0x1000 | Declared synthetic; not present in the source code.                               |
> | ACC_ANNOTATION | 0x2000 | Declared as an annotation interface.                                              |
> | ACC_ENUM       | 0x4000 | Declared as an enum class.                                                        |
> | ACC_MODULE     | 0x8000 | Is a module, not a class or interface.                                            |

After that are the indices in the constant pool of the `Constant_Class`s storing this class (`Main` in this case) 
and the superclass (`java/lang/Object` in this case).

Then after that are the number of interfaces, list of interfaces, number of fields, list of fields, number of methods, list of methods, number of attributes and the list of attributes.
I'm being (very) vague here as the tutorial doesn't cover beyond constant pools, but I'm laying a basic foundation.

Reading the [JVM specifications](https://docs.oracle.com/javase/specs/jvms/se19/html/jvms-4.html) will give you all the knowledge you need.

## Part 7: The practicality of this knowledge
**Q.** Do I need to know this? <br />
**A.** Not really.

**Q.** Will this help me get many jobs? <br />
**A.** Nope.

**Q.** Does this have a large use case? <br />
**A.** Not at all.

**Q.** Should I have put this at the top? <br />
**A.** Enjoy the free knowledge :)!




