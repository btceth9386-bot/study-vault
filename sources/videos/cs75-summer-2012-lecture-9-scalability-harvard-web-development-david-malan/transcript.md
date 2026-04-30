# CS75 (Summer 2012) Lecture 9 Scalability Harvard Web Development David Malan

Welcome back to Computer Science S75.

This is lecture nine, our very last.

It has been a pleasure having everyone in the course this semester.

So tonight we talk about scalability.

So we try to revisit some of the topics that we looked at earlier

in the semester and think about how we can deploy applications,

not just on, say, a virtual machine, on your laptop or desktop,

as we've been doing with the appliance, but how you can scale

to servers on the internet and, indeed, multiple servers on the internet

so that you can handle hundreds or thousands or tens of thousands

or even more than that in theory.

So some of the issues that we'll inevitably encounter

is how to go about doing this.

So when it comes time to put something on the internet,

recall from lecture zero that we talked about web hosts.

So this is by no means a list of recommendations, per se.

It's just some representative ones that we happen to recommend,

if only because the teaching fellows and I have had prior experiences

with these particular vendors.

But you can Google around, and you can see

that there's many, many, many different options these days.

However, among the takeaways, hopefully, from the summer thus far

has been, what kinds of features should you

be looking for or expecting minimally in any web hosting

company that you might choose?

And in fact, not all of these even have those features, necessarily.

Scott?

The accessibility, I mean, in some countries, it's all IP address.

For example, I have a server which is running on the GoDaddy,

but some of my friends don't access GoDaddy's hosting server.

So I have to switch to the blue code.

Interesting.

OK, good.

So if your country or your work or really any network that you happen to be on

or people that you know happen to be on block access to certain IP ranges,

among them, for instance, GoDaddy's in this case.

YouTube is a popular thing to block.

Facebook is a popular thing to block.

That can be a sticking point.

So doing a bit of due diligence or testing first can be a good thing.

What else should you look for in a hosting company?

Isaac?

SFTP.

Good.

SFTP in contrast with what?

FTP and why?

Because SFTP is secure.

OK, good.

So the S literally stands for secure.

And what that means is that all of your traffic is encrypted.

And this maybe isn't a big deal for the files that you're transferring.

Because after all, if you're uploading GIFs and JPEGs and video files that

are meant to be downloaded by people on the web, well,

then who really cares if you encrypt those between your machine

and the server?

But it is important to have what?

Data encrypted.

Jack?

Usernames, passwords, and passwords.

Exactly.

Usernames and passwords, right?

I mean, that's one of the biggest failings of something like FTP,

which granted is a fairly dated or older protocol,

is that it sends also your username and password in the clear,

which means anyone sniffing wirelessly around you,

anyone sniffing the wired network between point A and B

can see in the clear what your username and password are.

Yeah?

We looked at some hosting companies that offer unlimited everything

for a really low price.

OK, good.

That could be due to virtual hosting.

Good.

If you want to implement a system that can grow by itself,

you maybe don't want to share the same server with many others.

Good.

So DreamHost in particular, I think we pulled up their feature list.

And it was ridiculous how many features they give you.

Unlimited bandwidth, unlimited storage space, unlimited RAM,

or something like that.

And that just can't possibly be real if you're only paying like $9.95 a month.

So there's some catch.

And in general, the catch is that they're making that offer to you

and to hundreds of other customers, all of whom might be on that same machine.

So you're contending now for resources.

And the reality is they're probably banking in the fact

that 90-something percent of their customers

don't need that many resources.

But for the one person or two persons that do,

probably going the way of a shared host is not necessarily

in your best interest.

Certainly not something to try to build a bigger business on.

And so there's alternatives to things like web hosting companies.

There's VPSs, a virtual private server that you

can essentially rent for yourself.

And what's the fundamental distinction between a VPS and a shared web post?

Axel?

Well, a VPS is like our Fedora Linux.

It's a virtual machine running on a box, but it's completely its own system.

OK, good.

Well, and so to be clear, the operating system

is largely irrelevant since stream hosts and shared web hosts

could also be running Fedora or any operating system.

But what's key is that you get your own copy of Fedora or Ubuntu

or whatever operating system they happen to be running.

Because in the world of VPSs, what they do

is they take generally a super fast server with lots of RAM, lots of CPU,

lots of disk space, and they chop it up into the illusion of multiple servers

using something called a hypervisor, something

like a product from VMware or Citrix or other companies.

And even open source providers have platforms

that allow you to do this, run multiple virtual machines

on a physical machine.

And so in this world, you're still sharing resources,

but in a different way.

You're instead getting some slice of hardware to yourself,

and no one else has user accounts on that particular virtual machine.

Now with that said, the system administrators,

the owners of the VPS company, they themselves,

depending on what hypervisor they're using,

they might actually have access to your virtual machine and to your files.

And frankly, if you have physical access to the machine,

you undoubtedly have access to your files.

Because they can always reboot the virtual machine, for instance,

in what's called single user mode or diagnostic mode.

And at that point, they're not even prompted for a root password.

So realize that even when you're using a VPS,

your data might be more secure, more private from other customers,

but definitely not the web hosting company itself.

If you want even more privacy than that,

you're probably going to have to operate your own servers

that only you or your colleagues have physical access to.

So here's just a list of some of the popular VPS companies.

There is one catch.

In order to get these additional features or these properties in a VPS,

you generally pay more.

So instead of $10 a month, $20 a month, you're

probably starting at $50 a month or something like that,

maybe even in the hundreds, depending on how much you

want in the way of resources.

And toward the end of today, we'll talk about one

particular vendor of VPSes, namely Amazon Web Services, Amazon EC2.

They're Elastic Compute Cloud that essentially

lets you self-service and spawn as many virtual machines as you want,

so long as you're willing to pay some number of cents per minute

to have that virtual machine up and running.

And it's actually a wonderful way to plan for unexpected growth,

because you can even automate the process of spawning

more web servers, more database servers, if you happen to suddenly

get popular, even overnight, or because you've been slash-dotted

or posted on Reddit or the like.

And then you can have those machines automatically power off

when interest in your product or website has started to subside.

All right, so suppose you are the fortunate sufferer

of a good problem, which is that your website all of a sudden

is super popular.

And this website has maybe some static web content, HTML files,

GIFs, and the like, dynamic content like PHP code,

maybe even some database stuff, maybe some database stuff like MySQL.

Well, how do you go about scaling your site

so that it can handle more users?

Well, the most straightforward approach is generally

what's called vertical scaling, vertical in the sense

that, well, if you're running low on RAM,

or you're kind of exhausting your available CPU cycles,

or you're running low on disk space, what's

the easiest, most obvious solution to that problem?

Axel.

AUDIENCE MEMBER 2 Get a better processor and more RAM.

Good, get more RAM, more processor, more disk space,

and just throw resources, or equivalently money, at the problem.

Unfortunately, there is a catch here.

There's sort of a ceiling on what you can do.

Why?

Why is vertical scaling not necessarily a full solution?

AUDIENCE MEMBER 3 Well, you can only upgrade one machine so much

after a while, you can't upgrade it more.

DAVID J. MALANYIK Yeah, exactly.

There's some real world constraints here,

where you can only buy a machine that's maybe 3 gigahertz these days,

and maybe only has a handful of, maybe a couple dozen CPUs or cores.

But at some point, you're either going to exhaust

your own financial resources, or just the state of the art in technology.

Because just the world hasn't made a machine that

has as many resources as you need.

So you need to get a little smarter.

But at least within here, you have some discretion.

So in terms of CPUs, these days, most servers have at least two CPUs,

sometimes three or four or more.

And in turn, each of those CPUs typically has multiple cores.

In fact, most of the laptops you guys have here these days

are generally at least dual core, sometimes even quad core,

which means that you effectively have the equivalent of four CPUs,

or four brains, inside of your computer,

even though they're all inside of the same chip, essentially.

What does that mean concretely?

It means if you have a quad core machine,

your computer can literally do four things at once.

Whereas in yesteryear, when you had single core, single CPU machines,

they could only do one thing at a time.

And even though we humans seem to think that you're simultaneously printing

something, you're pulling up a Google Map, you're getting email,

and all of this stuff seems to be happening simultaneously,

the reality is the operating system is scheduling each of those programs

to get just a split second of CPU time before giving another program,

then another program, a split second of CPU time.

And we humans are just so slow relative to today's processors

that we don't even notice that things are actually

happening serially, as opposed to in parallel.

But when you actually have quad core, especially in a server,

that means whereas in yesteryear, with a single core machine,

you could handle one web request at a time,

now, for instance, you could handle at least four at a time,

truly in parallel.

And even then, a server will typically spawn

what are called multiple processes or multiple threads.

So in reality, you can at least give the impression

that you're handling many more than even four requests per second.

So in short, machines these days have gotten more and more and more CPUs,

as well as more cores.

And yet the funny thing here is that we humans also

aren't very good at figuring out what to do with all of this available

hardware, right?

Most of you, even if you have a dual core machine,

you don't really need a dual core machine to check your mail

or to write an essay for school, right?

You were able to do that five, 10 years ago with far fewer

computational resources.

Now in fairness, there's bloat in software and Mac OS and Windows

and Office are just getting bigger and bigger.

So we're using those resources.

But one of the really nice results of this trend

toward more and more computational resources

is that the world has been able all the more easily to start

chopping up bigger servers into smaller VPSs.

And indeed, that's how Amazon and other cloud providers, so to speak,

are able to provide people with this self-service capability,

as we'll discuss a bit later.

So within these things, there are a few things you have discretion over.

If you've ever built a computer, you might be familiar with Parallel ATA

or IDE or SATA or SAS.

Anyone?

Axel, what are these referred to?

AXEL DORFMANN-WILSON Yeah, SATA has to do with hard drives.

OK, good.

So SATA has to do with hard drives.

In fact, all three of those have to do with hard drives.

Years ago, Parallel ATA or IDE hard drives were very much in vogue.

You might still have them in older computers.

These days, desktop computers pretty much,

but you wouldn't buy a new Parallel ATA drive these days.

Instead, you'd most likely get a SATA drive,

whether 3.5 inch for a desktop or 2 and 1 half inch for a laptop.

And if you have servers or you have lots of money and a fancy desktop

computer, you can go with a SAS drive.

SAS is Serial Attached SCSI, and this really just boils down to faster.

For instance, whereas Parallel ATA and SATA drives typically

ran at 7,200 RPMs per minute, revolutions per minute,

SAS drives, anyone know what they typically spin at?

And for those unfamiliar, inside of a mechanical hard drive,

there is a one or more metal platters that literally spins,

much like an old school record player where the bits are now stored.

What speed does a SAS drive spin?

It's more than 7,200 RPM.

Excellent.

AUDIENCE MEMBER 15,000.

Yeah, so 15,000 is where they would typically perform.

Sometimes 10,000, but 15,000.

So just twice as fast, so that alone gives you a bit of a speed bump.

Of course, it comes at a price, literally, more money,

but that's one way of speeding things up.

So oftentimes, what people will do is for a given website

that they're creating, if it has a database,

databases tend to write to disk quite a bit.

Every Facebook update requires writing to disk

and then reading back out some number of times.

So really, where you might be touching disk a whole lot,

people can throw things like SAS drives in their database

so that their data can be read or written even more quickly.

And what's even faster than mechanical drives these days?

Axel?

AUDIENCE MEMBER 16, solid state drives.

Yeah, solid state drives, SSDs, which have no moving parts.

And as a result, electrically, perform much better

than mechanical drives.

But those, too, cost more money, and they tend to be smaller in size.

So whereas you can buy a four terabyte SATA drive these days,

3 and 1 1 for your desktop, you can buy, maximally,

a 768 gigabyte SSD these days for a lot more money, typically.

All right, so let's skip RAID for now.

So horizontal scaling.

So this is in contrast with what we just discussed, throwing money

and throwing more of everything at a problem.

Horizontal scaling is sort of accepting the fact

that there's going to be this ceiling eventually.

So why don't we instead architect our system in such a way

that we're not going to hit that?

Rather, we can kind of stay below it by even using not state-of-the-art

hardware and the most expensive stuff we can buy, but cheaper hardware.

Servers that might be a few years old, or at least are not the top of the line

so that they'll be less expensive.

So rather than get few or one really good machine,

why don't we get a bunch of slower, or at least cheaper, machines instead?

Plural number of machines.

So this is just a picture of a data center, which

is just meant to conjure up the idea of scaling horizontally

and actually using multiple servers to build out your topology.

But what does this actually mean?

Well, if you have a whole bunch of servers now, instead of just one,

what's the relationship now with lecture zero,

where we talked about HTTP and DNS?

The world was very simple a few weeks ago when you had a server

and it had an IP address.

And that IP address might have a domain name or host name associated with it.

And we told that story of what happens when you type in something.com,

enter on your laptop, and you get back the pages on that single server.

But now we have a problem if we have a whole aisles worth of web servers.

Axel?

Well, you're going to have to have a way to treat each request so that it

doesn't end up at one machine.

So that your request can be distributed over all machines.

OK, good.

So now if we get an inbound HTTP request,

we somehow want to distribute that request over all of the various web

servers that we might have, whether it's two web servers or 200.

The problem really is still the same.

If it's more than one, we have to somehow figure that out.

So let me put up a fairly generic picture here.

Let me flip past those to this guy here.

So if we have a whole bunch of servers on the bottom here, server 1, 2,

dot, dot, dot, and on the top we have some number of clients,

just random people on the internet, we need to interpose now

some kind of black box that's generally called a load balancer,

depicted here as a rectangle, so that the traffic coming

from people on the internet is somehow distributed or balanced

across our various back end servers, so to speak.

So it might still be the case that server 1 and 2 and so forth

have unique IP addresses.

But now when a user types in something.com and hits Enter,

what IP address should we return?

How do we go about achieving the equivalent

of this man in the middle who can somehow balance load across all end

servers?

Well, return the IP address of the load balancer,

send the request to the load balancer, and then

let the load balancer handle which computer to send it to.

OK, good.

So instead of in DNS returning the IP address of server 1 or server 2

or server dot, dot, dot, you could instead

return the equivalent of the IP address of this black box, the load balancer,

and then let the load balancer figure out

how to actually route data to those back end servers.

So that's actually pretty clean.

So now if the load balancer has a public IP address,

the back end servers now technically don't even need public IP addresses.

They can instead have private addresses.

And what was the key distinction between public and private IPs

back in lecture 0?

Anyone over here?

Yeah?

Lewis?

The rest of the world can't see private IP.

Exactly.

So the rest of the world, by definition of private,

can't see private IP addresses.

So that seems to have some nice privacy properties

in that if no one else can see them, they can't address them.

So those servers, just by nature of this privacy,

can't be contacted, at least directly, by random adversaries,

bad guys on the internet.

So that's a plus.

Moreover, the world has been running out of version 4 IP addresses.

The 32-bit IP address has come into scarcity for some time now.

So it's just hard, or sometimes expensive,

to get enough IP addresses to handle the various servers that you might buy.

So this alleviates that pressure.

Now when we need one IP and not multiple for our servers,

because we can give these back end servers a number like 192.168,

which most of you have in your home routers probably, or 10.something,

or 172.16 something, all of those to mark

the start of a private IP address.

So that works.

All right, so the load balancer has its own IP address now.

It gets a request from some client on the internet.

How, using jargon from lecture 0 onward,

can the load balancer decide or get that data to one of the back end

servers?

How could we go about implementing that?

Axel?

Well, you would probably first want to figure out

which server to send it to.

So you'd want to check if somebody has available CPU cycles that they're not

using.

And once you see that there's one server with enough CPU cycles

to handle that request, it's a local request.

The same request, but locally inside your server network

to that machine, get back whatever it is that the client requested,

and then the load balancer sends it back.

Excellent.

So this request arrives then at the load balancer.

The load balancer decides to whom he wants to send this packet, server 1

or 2 or dot, dot, dot.

And you can make that decision based on any number of factors.

So Axel proposed doing it based on load, like who

is the busiest versus the least busy.

Odds are I should send my request to the least busy server

in the interest of optimizing performance all around.

So let's assume that there's some way, as demarcated by those black arrows,

of talking to those back end servers and saying, hey, how busy are you?

Let me know.

So now the load balancer figures out it wants

to send this particular request to server 1.

So it sends that request to server 1 using similar mechanisms, TCP, IP,

much like the packet, how it traveled to the load balancer in the first place.

The server then gets the packet, does its thing, and says, oh,

they want some HTML file.

Here it is.

The response goes to the load balancer.

The load balancer then responds to the client, and voila.

So that works.

What are some alternatives to load balancing based

on the actual load on these servers?

So load, in general, refers to how busy a server is.

So what's an even simpler approach than that?

Because that, frankly, that sounds a little complex.

We've not talked at all about how one device can query another

for characteristics like how busy are you, even though it's possible.

Axel?

First, let me point out a dumb side with that.

You need to have every file that the website has on every server.

So if you would instead, say, have one server containing all the HTML

and one running and containing all the PHP, you would then see, well,

oh, OK, bad example.

One example, one server with all the images and one with all the HTML.

So a client requests an image.

It sends it to the image server.

And it's an HTML request to the HTML server.

OK, good.

So the implication of the previous story that Axel told

is that under this model, server 1, 2, and so forth all need to be identical,

have the same content, which is nice in that then it doesn't matter

to whom you send the request.

The downside is now you're using n times as much disk space

as you might otherwise need to.

But that's perhaps the price you pay for having this redundancy

or to having this horizontal scalability.

Or instead, you could have dedicated servers.

These are for HTML.

These are for GIFs.

These are for movie files and the like.

And you could do that just by having different URLs, different host names.

This is, for instance, images.something.com.

This is videos.something.com.

And then the load balancer could take into account the host HTTP header

to decide which direction it should go in.

So that could work for us.

All right, so what's an even simpler heuristic than asking a back-end server

how busy are you right now?

If you have no idea how to do that, how instead

could we balance load across an arbitrary number of servers?

Think again back to lecture zero.

You can do all of this with only lecture zero under our belt.

So let's quickly tell the story.

I type in something.com into a browser.

I hit Enter.

What happens?

Jack?

AUDIENCE MEMBER 2 We create a packet to send.

DAVID J. MALANYIK OK, packet to send.

To whom do we send it?

AUDIENCE MEMBER 2 We send it to some place that will determine the IP

address of where we're sending it to.

DAVID J. MALANYIK OK, good.

Something that will determine the IP address of where we're sending it to.

What's that thing called?

Isaac, what's that called?

AUDIENCE MEMBER 2 Router.

DAVID J. MALANYIK Not router.

Routers get involved, but the DNS server, domain name system server.

So that server in the world, a whole bunch of them,

whose purpose in life is to translate host names to IPs and vice versa.

So I'm going to pause the story there.

That seems to be an opportunity now for us to return something.

Yeah?

AUDIENCE MEMBER 3 Could you do some DNS tricks and return different IP

addresses based on what the user requested?

DAVID J. MALANYIK Good.

So this black box, this load balancer, maybe it's just a fancy DNS setup

whereby instead of returning the IP address of the load balancer itself,

maybe instead the DNS server just returns the IP address of server one

the first time someone asks for something.com.

And the next time someone requests something.com,

it returns the IP address of server two, followed by server three,

followed by dot, dot, dot, and then wrapping around eventually

to server one again.

So this is actually generally called round robin.

And you can do this fairly easily.

This is just a snippet of a popular DNS server called Bind, Berkeley

internet name demon, I believe is the D.

And this just suggests that if you want to have multiple IP addresses for a host

name called dub, dub, dub, you mention a, which denotes a record,

in just refers to an in pointer here.

But a is the same as in lecture zero.

And then you just enumerate the IP address one after the other.

And by default, this particular DNS server, a very popular one,

Bind, will return a different IP address for each request.

So that's nice.

It's simple.

Again, uses only some knowledge from lecture zero,

even though granted you have to know how to configure the DNS server.

But you don't need any fancy bi-directional communication

with the back end servers in this model.

So that's nice.

But there's a price we pay for this simplicity.

If we only do round robin, where again, we just spit out a different IP

address each time.

And let me make this more concrete, just so this isn't quite as abstract.

Let me open up a terminal program here and do nslookup for name server

lookup of google.com.

This is exactly what Google does, at least in part.

Their load balancing solution is more sophisticated than this list suggests.

But indeed, Google's DNS server returns multiple IP addresses each time.

So if this is so simple to implement, what's the catch?

Axel.

Well, it's not a very smart solution, because the case

could be that one server gets all of the really tough and hard requests

that take a lot of processing power.

And the other ones just get the PDHTML files.

So there's no way to know that.

Good.

So just by bad luck, one of the servers could just

get a real power user, someone who's really doing something computationally

difficult, like, I don't know, what's a good example?

Sending lots of mail, where someone else is just kind of logging in

and poking around at a much slower rate.

And we could come up with even more sophisticated examples than that.

But over time, server one might just happen

to get more heavyweight users than other servers.

So what's the implication?

Well, round robin is still going to keep sending more and more users

to that server one nth of the time, just by nature of round robin.

So that's not so good.

What else causes problems here?

Or what else breaks, potentially?

So back to the lecture zero story.

I type something.com.

I hit Enter.

My browser sends a request to the DNS server, or my operating system

sends a request to the DNS server, gets the IP address.

And in this model, it's the IP address of one of these servers.

Then I send my packet, as Jack proposed, to that particular server,

get back a response.

Story ends.

But then a few seconds later, I visit another link on something.com

and hit Enter.

Which part of the story now changes?

Jack?

to send to the same server of a cluster as it sends to a new server?

Good question.

Does that have to do with where it's coming from?

So how does the story change?

And that'll give us the answer here.

Axel?

Well, it has to send it to a new server, otherwise it's

bound to run on a new server.

Oh, ideally, yes.

So if you want a truly uniform distribution across all end servers,

then the DNS server has to return another response.

And I'd argue the DNS server will return a different response

the next time it is queried.

But why?

Because it's saved.

Saved or?

No, but the IP address is stored.

Where?

If you have a whole concession.

Otherwise, it's really useless to query the DNS server for the same thing

over and over again.

Good.

So recall these caches.

Back in lecture zero, we talked about the implications

of the good parts of caching, whereby, as Axel's proposing,

there's no reason for Chrome or IE to send the same DNS request

every single time you click a link on something.com.

That would just be a waste of time.

You're going to lose some number of milliseconds every time that happens,

or worse yet, a second or two.

So instead, your operating system typically caches these responses.

Your browser typically caches these responses as well.

And so you just don't need to do those lookups.

So if you do happen to be that power user who's

doing a heck of a lot of work of whatever sort on server one,

the next guy is going to be sent to server two,

not you with your subsequent requests.

So caching, too, can contribute to a disproportionate amount

of load on certain servers, largely due to bad luck.

Indeed, in DNS, we didn't spend much time on this particular detail,

but there's typically expiration times, TTLs,

time to live values associated with an answer from a DNS server.

And that's typically an hour or five minutes or a day.

It totally depends on who controls the DNS server what that value is.

But that suggests, too, that if you are this power user on server one,

it might be a few minutes or hours or even days

until you get assigned to some other server,

simply because your TTL has expired by then.

So it's nice and simple.

We can do it with a simple configuration change,

but it doesn't necessarily solve all of our problems.

So in fact, the approach Axel proposed first

is actually pretty good, whereby you don't use DNS-based round robin.

Rather, a more sophisticated approach would

be to let the load balancer decide to whom to send you in the back end.

And the load balancer can make that decision

using any number of heuristics.

It could even use round robin or randomness,

because at that point, you don't have to worry about caching issues,

because the DNS server has only returned one IP.

But that still leads you to the risk that you'll

be putting too much load on some server.

So we could take, for instance, server load into account at that point.

But there is something else that breaks.

If we fast forward mid-semester to when we started talking about cookies

and HTTP and sessions in PHP, to spark discussion,

I propose that sessions have just broken in PHP.

If our back end servers are PHP-based websites

and they are using the session super global,

load balancing seems to break this model.

Why, Jack?

Because now the different servers have different people's sessions.

So although one might have my session, if I then

am redirecting from server one to server two,

the server two might not have my session.

Exactly.

So sessions, recall, tend to be specific to the given machine.

We saw examples involving slash temp, which

is a temporary directory on a Linux system,

where sessions are typically saved as text files, serialized text files.

So that means, though, that your session might

be sitting on the hard drive of server one.

And yet, if by random chance, you are sent by a round robin to server two

or server three, instead of server one, in the worst case,

you're going to see the same website, but you're

going to be told to log in again, for instance,

because that server doesn't know that you've logged in.

Well, OK, fine, you kind of bite your tongue

and you type in your username and password again and hit Enter.

And suppose you're a really good sport and you do this for all end servers.

You have no idea why something.com keeps prompting you to log in.

But eventually, you will have a session cookie on all of those servers.

The catch then, though, is that if something.com is an e-commerce site

and you're adding things to your shopping cart,

now you literally have put a book in your cart over here,

a different book in this card, a different book in this card.

And when you check out, you can't check out the aggregates.

So this is a very non-trivial problem now.

Axel.

But this wouldn't happen if you had dedicated machines distributing

dedicated files, one machine running PHP and then one machine serving

all the images.

Very true.

So if we have horizontally scaled in the sense

that we factored out disparate services, this is our PHP server,

this is our GIF server, this is our video server,

then indeed this problem would not arise because presumably all the PHP

traffic would get routed to the PHP server.

But an obvious pushback to that solution is what?

Isaac?

Well, if one of them crashes, you lose all the images.

OK.

Good.

So there's no redundancy, which is not good for uptime if anything breaks.

Axel?

And also, well, at some point in time, if you get popular enough,

that one PHP server is not going to be able to handle everything.

Good.

Then the story is the same.

As soon as you get popular, you have too much load for a single PHP server.

Then we have to solve this problem anyway.

So how do we go about solving this problem?

This seems to be a real pain, this one.

And to be clear, the problem now is that in as much as sessions

are typically implemented per server in the form of a text file

like we saw in slash temp, then you can't really use round robin.

You can't really use true load balancing, taking

into account each server's load.

Because you need to make sure that Alice, if she's initially sent to server

one, subsequently gets sent to server one again and again and again

for at least an hour or a day or some amount of time

so that her session is useful.

Jack?

Is there a way to create a server that's specially

dedicated to store everyone's sessions and all the sessions

that are started there?

Excellent.

Yes, so absolutely.

We could just continue this idea of factorization

and factor out not the various types of files,

but a service like session state.

So if we instead had a file server, like a big external hard drive,

so to speak, that is connected to all of the servers, one and two

and three, so that any time they store session data, they store it there.

Instead of on their own hard drive, then this way we could share state.

So indeed, that could be a solution here.

Axel?

I don't know if the load balancer has that function,

but maybe instead of having an extra server that all the other servers

need to query, what if the load balancer, because all traffic goes

through that anyhow, what if the load balancer stores the session?

OK, so that's not bad at all.

So we already have a man in the middle here.

It's a black box, but there's no reason it couldn't

be a server with hard disk space.

So why not put the sessions on the load balancer?

That could absolutely work.

So let me be difficult then, and whether we put the sessions in the load

balancer or whatever, it's no longer a load balancer then.

It's obviously doing more.

It's more of a server that happens to be balancing load and storing sessions.

Whether we put sessions there in that black box

or elsewhere in a new box on the screen,

we seem to have introduced a weakness now in our network topology.

Because what if that machine breaks?

It would seem to be the case that even though we have n servers, which

in theory, those guys are never all going to die at once,

assuming that it's not the power or electricity or something stupid

like that that's somehow related to all of them.

But odds are they're not all just going to up and die simultaneously.

So we have really good redundancy in our server model right now.

But as soon as we introduce just a database or file server for our

sessions, if that guy dies, then what was the point of spending all this

money on all these back end servers?

Our whole site goes down, because we have no ability

to remember that people are logged in.

If we can't remember they're logged in, no one can buy anything.

So how do we fix that problem?

So we've solved one problem.

But if you think of that sort of old visual

where you have a garden hose with lots of leaks in it,

and you plug one of them with one hand, all of a sudden

a new leak springs up elsewhere.

That's kind of what's happened here.

We've solved the problem of shared state.

But now we've sacrificed some robustness, some redundancy.

How do we now fix the latter?

Axel?

It's probably not the solution you're looking for.

But the hardware on your load balancer could

be built such that any such hard drive is typically missing RAID 5.

OK, good.

So we could just use a sort of different approach to storing our data.

And rather than just store it on the hard disk as usual,

we could use something called RAID.

So actually, this is a good way to tie in the thing we skipped over

a moment ago.

Let me just pull up something to write on here.

So redundant array of independent disks is a technology more succinctly known

as RAID.

RAID can actually be used in desktop computers these days,

even though it's not all that common.

Some companies like Dell and Apple make it relatively easy

to use RAID on your system.

And what does this mean?

Well, RAID can come in a few different forms.

There's something called RAID 0, there's something called RAID 1,

there's something called RAID 5, there's something called RAID 6,

there's something called RAID 10, and there's even more.

But these are some of the simplest ones to talk about.

So all of these variants of RAID assume that you

have multiple hard drives in your computer,

for different purposes, potentially.

So in the world of RAID 0, you typically have two hard drives

that are of identical size, terabyte, two terabytes, 512 gigabytes,

whatever it is, two identical hard drives.

And you do what's called stripe data across them,

whereby every time the operating system wants to save a file,

especially big files, it will first write to this drive a bit,

then to this one, then to this one, then to this one.

The motivation being, these hard drives are typically

large and mechanical, with spinning platters, like we discussed earlier.

And so it might take this guy a little while

to write out some number of bits.

Now, that's going to be a split second in reality,

but that's a split second.

We don't really have that.

So striping allows me to write some data here, then here, then here,

then here, then here, then here, effectively doubling the speed at

which I can write files, especially large ones to disk.

So RAID 0 is nice for performance.

However, RAID 1 gives you a very different property.

With RAID 1, you still have two hard drives,

but you mirror data, so to speak, across them.

So that any time you write out a file, you

store it both places, simultaneously.

There's a bit of a gap between what you're

both places simultaneously.

There's a bit of performance overhead to writing it in two places,

albeit in parallel.

But the upside now is that either of these drives can die,

and your data is still perfectly intact.

And it's actually an amazing technology, because even if you just

have this in your desktop computer, you have two drives, one of them

dies just because of bad luck.

There's a defect, or it's multiple years old, and it just upped and died.

So long as the other one is still working,

the theory behind RAID is that you can then

run to the store, buy another hard drive that's at the same size or bigger,

plug it into your computer, boot back up, and typically, automatically,

the RAID array will rebuild itself, whereby all of the data that's

on the remaining drive will copy itself automatically over to the new one.

And after a few minutes or hours, you're back to a safer place,

whereby now even the other drive can up and die.

Sometimes you have to run a command or choose a menu option to induce that,

but typically it's automatic.

You can do it even sometimes in some machines while the computer is still

on, so you don't even have to suffer any downtime.

So that's great.

RAID 10 is essentially the combination of those two.

You typically use four drives, and you have both striping and redundancy.

So you sort of get the best of both worlds, but it costs you twice as much,

because you need twice as many hard disks.

RAID 5 and RAID 6 are kind of nice middle grounds with RAID 1,

or nice variants of RAID 1, whereby RAID 1 is kind of pricey, right?

Rather than buy one hard drive, I literally

have to spend twice as much and get two hard drives.

RAID 5 is a little more versatile, whereby I typically

have, say, three drives, four drives, five drives, but only one of them

is used for redundancy.

So if I get five 1 terabyte drives, I have 4 terabytes of usable space.

So I'm only sacrificing 1 5th, in that case, of my available disk capacity,

whereas in RAID 1, you're sacrificing 1 half, so 50% of it.

So RAID 5, you just get better economy of scale, whereby you can grow bigger,

and you still have some redundancy.

So in RAID 5, if you have three or four or five hard drives in the array,

one of them can die.

Any of them, you run to the store, put in a new one,

and you haven't lost any data.

RAID 6 is even better.

What does RAID 6 do, do you think?

Axel?

AXEL DORFMANN-WILSON

Exactly, in RAID 6, any two drives can die.

You still won't have lost any data, and so long

as you run to the store fast enough and put in one or both drives again,

you'll be good to go.

Of course, the price you pay with RAID 6 is literally another hard drive,

but at least now you can maybe sleep a bit better at night,

knowing that, man, two of my hard drives

has to die before I have to really worry about this.

So these are really nice technologies.

And so as Axel proposes here, the upside

of using something like that in whatever file server

we're storing our shared sessions is we can at least decrease

the probability of downtime, at least related to hard disks.

Unfortunately, it still has a power cord that someone could trip over

or the power supply could die.

It still has RAM that could go on the fritz, a motherboard that could die.

Any number of things could still happen,

but at least we can throw redundancy inside

of the confines of a single server.

And this can definitely help with our uptime and with our robustness.

And indeed, with actual servers that you would buy for a data center,

not so much the home, it's very common for computers

to have not only multiple hard drives and multiple banks of RAM,

they would often have multiple power supplies as well.

And it's actually a really cool technology there, too.

If one of your power supplies dies, you can literally pull it out,

the machine keeps running, you put in a new one,

and then it spreads the amperage across two power supplies

once both are back up and running, all very hot swappable.

Amazing technology these days.

And as an aside, if you still own a desktop computer,

no reason you shouldn't use RAID these days.

It is just very good practice, since it will

allow you to avoid downtime and data loss with higher probability.

But someone tripped over the power cord.

Someone tripped over both power cords in the case of redundant power supplies.

So Axel's solution, and even mine, with redundant power supplies

hasn't solved the problem of shared storage

becoming, all of a sudden, a single point of failure.

So what else could we do?

To still get the property of shared state.

So it doesn't matter what back end server I end up on,

but I still get to the ability to suffer some downtime.

Well, shared storage can come in a bunch of different ways.

So we talked, really, about things as a file server,

but this can be incarnated with very specific technologies.

And just to rattle them off, even though we won't talk about them

in much technical detail, Fibre Channel, FC,

is a very fast, very expensive technology

that you can use in offices and data centers, not so much the home,

to provide very fast shared storage across servers.

So that's just one type of file server, if you will.

iSCSI is another technology that uses IP, internet protocol,

and uses ethernet cables to exchange data with servers.

So that's a nice, somewhat cheaper way of having a shared file server that

can be used by multiple.

Actually, in the case of iSCSI, you typically

use it with single servers.

So let me retract that.

That is not a solution to our current cookie problem.

But what about MySQL?

We used that for a couple weeks.

MySQL seems to be a nice candidate, because it's already

a separate server, potentially.

Could not the back end servers just write their session objects

to a database?

They definitely could.

So just because we usually store things like user data,

and user generated data in a database, doesn't

mean we can't store metadata like our cookie information as well.

Or that too comes from users, though.

NFS, Network File System, this is just a protocol

that you can use to implement the idea that Axel proposed

of a shared file system.

It just means you've got one server, and you're

exposing your hard disk to multiple other computers.

But again, we haven't really solved the problem of downtime.

So what's the most obvious way of mitigating the risk

that your single file server will go down?

Axel?

AUDIENCE MEMBER 2.

Keep a copy of the sessions in other locations.

DAVID MALAN.

Good, right?

If you're worried about the one file server going down,

well, the obvious solution, even though money and some technical complexity,

we'll just get two.

Now, somehow you have to figure out how to sync the two,

so that one has a copy of the other's data and vice versa.

So let's actually come back to that issue.

It's generally known as replication, but it

is something we can potentially achieve.

But before we segue to distribution of things,

let's finish out this load balancer question.

So how do you go about implementing this black box?

Well, these days, you actually have a bunch of options.

In software, you can do things relatively easily

with a browser, pointing and clicking, using things like Amazon's Elastic

Load Balancer, a scenario for which we'll talk about a bit later.

HAProxy, High Availability Proxy, is free open source software

that you can run on a server that can do load balancing as well,

using either of the heuristics we discussed earlier, Round Robin,

or actually taking load into account somehow.

Linux Virtual Server, LVS, is another free piece of software you can use.

And in the world of hardware, people have made big business out

of load balancers.

Barracuda, Cisco, Citrix, F5 are some of the most popular vendors here,

most of whom are atrociously overpriced for what they do.

So case in point, Citrix is a popular company that sells load balancers.

Take a guess as to what a load balancer might cost you these days.

It's a highly variable range, but there's different models.

But take a guess.

How much did that black box cost?

Isaac?

AUDIENCE MEMBER 1.

In the thousands?

DAVID MALAN.

Definitely in the thousands, indeed.

In fact, we have a small one, relatively speaking, on campus

that was $20,000.

And guess what?

That one's cheap.

So you can literally spend on these kinds of things.

Granted, this is not what the costs that await you right

after the semester ends today.

But $100,000 for a load balancer, or even generally a pair of load balancers

so that either of them can die and the other one can stay alive.

So in the world of enterprise hardware, these ideas we're talking about

are ridiculously priced, typically because of support contracts

and the like.

So just realize software is number one on the list

because there are other ways to achieve this much more inexpensively.

Indeed, for years, one of the courses I teach,

we used HAProxy to balance load because it was so relatively easy to set up

and 100% free.

So realize these same ideas can be both bought and set up on your own

quite readily these days.

All right.

Let's pause here.

And when we come back, we'll take a look at some issues of caching,

of replication in databases, and also how we can speed up PHP a bit.

Let's take our five-minute break here.

All right.

We are back.

And I almost forgot.

We have one other solution to this problem of the need for sticky sessions.

Sticky sessions meaning that when you visit a website multiple times,

your session is somehow preserved, even if there are multiple back-end servers.

So shared storage was the idea we really vetted quite a bit.

And we didn't quite get to a perfect solution

since even though we factored out the storage

and put everyone's cookies or session objects on the same server,

it feels like we need some redundancy.

But we'll come back to that in the context of MySQL in just a bit.

But what about cookies?

I propose that cookies themselves could offer a solution

to the problem of sticky sessions.

And again, sticky session means even if you visit a website multiple times,

you're still going to end up with the same session object,

or more specifically, you're still going to end up on the same back-end

server.

Axel?

AUDIENCE 2 Either store which server you want to go to in a cookie.

DAVID MALAN.

OK.

AUDIENCE 2 Or store everything in cookies.

But that's not a good solution.

DAVID MALAN.

OK, yeah.

So storing everything in cookies is probably bad.

Because one, then it's really starting to violate privacy.

Because rather than store a big key, you're

going to store the ISBNs of all of the books in your shopping cart.

And that might be fine.

But it feels like your roommates and family members

don't need to know what is in your cookies.

Moreover, cookies typically have a finite size of a few kilobytes.

So there's definitely going to be circumstances

in which you just can't fit everything you want to in the cookie.

So an interesting idea, but probably not the best.

So you could store the ID of the server in a cookie

so that the user, the second and third and fourth times

they visit your website, as by following links or coming back

some other time, they are going to present the equivalent of a hand

stamp saying, hey, I was on back end server one.

Send me there again.

So that's a pretty nice idea.

There is at least one downside here.

What do you not like, potentially, about this idea

of storing in a cookie that gets put on the user's browser

that they subsequently transmit back to you

the number of, or the ID of, the server to which they should be sent?

Maxwell?

AUDIENCE MEMBER 2.

Well, for one, expiration.

DAVID MALAN.

Expiration in what sense?

AUDIENCE MEMBER 2.

Well, a cookie expires after two.

DAVID MALAN.

OK.

So eventually, a cookie is going to expire.

Though, we saw a couple lectures ago, we

could make it expire in 10 years if we really wanted to.

And frankly, we're never going to avoid that.

Even if we had a single server, cookies could eventually expire.

So at least that's not a new problem.

So I'm not too worried about expiration now.

Because that's not a problem new to us, simply because of load balancing.

Does anything not feel right about storing

the ID of the server in the cookie?

Lewis?

AUDIENCE MEMBER 3.

What if the IP changes?

DAVID MALAN.

Yeah, so if we just put the back end IP, so the private IP address

in the cookie, what if the IP changes?

What if that, what if the IP changes?

So that's a little problematic.

And it's also one of these principled things.

You don't really need to reveal to the world what your IP address scheme is.

It's not necessarily something they could exploit,

but it's just the whole world doesn't need to know that.

Moreover, we can implement the same idea by still storing

a cookie on the user's computer.

But why don't we take the PHP approach of,

let's just store a big random number, and then have the load balancer

remember that that big random number belongs to server 1.

And this other big random number belongs to server 2, and so forth.

So a little more work on the load balancer.

But in this way, then, we're really not putting

any states that might change or might be a little privacy revealing

on the actual user's computer.

Moreover, we also take away the ability for them

to spoof that cookie just to get access to some other server.

Now, whether or not they could do anything with that trick is unclear.

But at least we take away that ability altogether, so there's no surprises.

All right, so cookies, indeed, are something

that these black boxes of load balancers

tend to do, whereby you can configure them to insert a cookie themselves.

It doesn't just have to be a back-end web server that generates cookies.

The load balancer, similarly, could be inserting a cookie with the set cookie

header that the end user then subsequently sends back,

so that we can remember what back-end server to send the user to.

Now, if the user has cookies disabled, well,

then this whole system breaks down.

But again, so does a lot of functionality

we've discussed thus far this semester.

But there are sometimes some workarounds.

So a word on PHP.

PHP and interpreted languages, in general,

tend to get a bad rap for performance, because they tend not

to be as high-performing as a compiled language, like C++ or C or the like.

However, there are some ways to mitigate this.

There's this notion of PHP acceleration, whereby you can run a PHP program,

the source code, through php.exe, the interpreter on the system.

And it turns out that PHP does typically compile that file,

in a sense, down to something that's more efficiently executed,

much like Java compiles something down to something called byte code.

But typically, PHP throws the results of that compilation away,

whereby it does it again and again for every subsequent request.

However, with relatively straightforward and freely

available software, you can install a PHP accelerator.

Here are just four possibilities that essentially

eliminate that discarding of the PHP opcodes

and instead keep them around.

So in other words, the first time someone visits your site,

the PHP file is going to be interpreted and some opcodes

for performance generated.

But they're not going to be thrown away.

Because the next time you or someone else visits the site,

that PHP file is not going to have to be reparsed and reinterpreted.

The opcodes are just going to be executed.

So you get the benefit of some added performance.

Now, the only gotcha is, if you ever change any of your .php files,

you have to throw away the cached opcodes.

But these various tools typically do that for you.

Python has a similar mechanism, where you'll get .py files,

or your source code files.

But .pyc files are the compiled.

compiled versions that can be executed more quickly.

So the same idea as at play here.

So this is one of these things that is relatively easy and free to enable and gives you all

the more performance, specifically the ability to handle all the more requests per second

in the context of a PHP-based website.

So what about caching, too?

Caching in general is a great thing.

It solved some of our DNS concerns early on, but it introduced others, because caching

can be a bad thing if some value has changed, but you have the old one.

But caching can be implemented in the context of dynamic websites in a few different ways.

So I propose that through HTML, through MySQL, and through something called memcached, we

can achieve some caching benefits here.

So this is a screenshot of one of the most 1990s websites out there, and this was not

even taken in the 1990s.

This was taken a couple years ago, and I just visited out of curiosity Craigslist today.

Still looks the same.

So what's interesting about Craigslist, though, is that it is a dynamic website, and that

you can fill out a form and post a for-sale ad or roommate ad or the like, and the website

does actually change, but if we zoom in on this, and it's going to be a little blurry

because of the screenshot, the URL that's up there is actually .html, even though it's

barely readable at this resolution, which is to suggest that Craigslist is apparently

accepting user input through forms, for instance, whoever wrote up this job advertisement some

time ago, but then Craigslist is spitting it out as a .html file, as opposed to storing

it where, or in what?

Axel?

Yeah, so this is in stark contrast to what we've done for Project Zero, Project One,

using PHP as the back-end, whereby you store data like this, like server-side, in maybe

an XML file or, more realistically, in a, in a MySQL database or similar, and then you

generate a page like this dynamically.

So why is Craigslist doing this, apparently?

Could just be they're stuck in the nineties, but there's a compelling reason, too.

Axel?

Well, if they store the actual HTML file, then they don't have to regenerate it every

time it's visited.

Yeah, exactly.

If they're storing the HTML file, they just don't have to regenerate it every time it's

revisited.

So this itself is caching.

It's not caching in any particularly fancy way.

You're just generating the HTML and saving it something called, like, something.html

and storing it on disk.

And the upside of this is that web servers, like Apache, are really, really, really good

and fast at just spitting out bits, just spitting out raw, static content, like a GIF, a JPEG,

an HTML file.

The performance optimizations these days generally relate to the languages, like PHP and Python

and Ruby, where you're trying to fine-tune performance.

But if all you have to do is respond to a TCPIP request with a bunch of bytes from disk,

that's relatively straightforward these days.

And so they're taking advantage of the performance, presumably, of serving up static content.

But this comes at a cost.

What's the downside of this file-based caching approach?

Someone else?

Nothing we've done thus far is sort of a complete win.

There's always a gotcha.

Lewis?

OK.

So space.

So we're storing it on disk.

And if you've ever posted on Craigslist, they're also storing it somewhere in a database because

they do let you go back and edit it.

It's just Craigslist is one of these sites where reads are probably much more common

than writes.

Indeed, when people visit Craigslist, they're probably flipping through reading pages as

opposed to posting lots and lots and lots of ads all at the same time.

So there's some redundancy there that's unfortunate.

Axel?

Yeah.

To just build upon that, you will be storing lots of code that you use on every page over

again.

Plus, it's not a very elegant solution to have a big folder on your server containing

10,000 files.

OK, good.

So there's redundancy.

Well, actually, with all these thousands of files, there's redundancy, too, just in the

basic stuff.

Like, you have the same HTML tag, the same body tag, the same link tag, the same script

in every single page if they're, indeed, just static HTML files.

So whereas you get some benefits of using something like PHP, and recall our MVC discussion

where we factored out template code, like the header and the footer, so that we stored

it one place and not thousands of places, Craigslist is kind of sacrificing that feature

and going with this instead.

So in the end, it's probably a calculated trade-off.

You get much better performance, presumably, from just sterving up the static content.

But the price you pay is more disk space.

But at the same time, for a few hundred dollars, you can typically get even bigger

hard drives these days.

So maybe that's actually the lesser of the evils.

But there is one gotcha.

There's another big gotcha here.

If you've generated tens of thousands of Craigslist pages that look like this, what's

the implication now?

And maybe why are they stuck in the 90s?

Well, I decide to add, well, change the background color.

Good.

Change the design entirely, which is necessary.

But I can't do that without editing each one of those 10,000 files.

And that could be done automatically.

But it's much harder than just editing a generic template that generates it.

Exactly.

If you want to change the aesthetics of the page and add a background color,

change the CSS, or make the font something other than Times New Roman,

it's non-trivial now.

Because assuming this is a fully intact HTML file with no server side include

mechanism, no require mechanism like you have in PHP, you have to now change

the background color in tens of thousands of files.

Unless maybe you at least put it in the CSS file.

But even then, if it's a less trivial change than color, suppose you want

to restructure the HTML of the page, then you really have to do a massive

find and replace, or more realistically, probably regenerate all 10,000 plus

pages.

And we latched onto 10,000 arbitrarily.

But it's a lot of pages in this case.

So upsides and downsides.

They're one of the few people on the internet who do this particular

approach.

But it does have some value.

And I think the last time I read up on statistics,

they get by with relatively little hardware as a result, which

is definitely compelling.

So MySQL query cache.

This is a mechanism that we didn't use.

But it's so easily enabled.

On a typical server with MySQL, there's a file called my.cnf for your

configuration file.

And you can simply add a directive like query cache type equals 1,

and then restart the server to enable the query cache, which

pretty much does what it says.

If you execute a command like select foo from bar where baz equals 1, 2, 3,

that could be slow the first time you execute it if you don't have

an index or if you have a really huge table.

But the next time you execute it, if the query cache is on

and that row hasn't changed, the response is going

to come back much more quickly.

So MySQL provides this kind of caching for identically executed queries,

which might certainly happen a lot if a user is navigating your website,

going forward and back quite a bit.

Memcache is an even more powerful mechanism.

Facebook has made great use of this over the years, especially initially.

Memcache is a memory cache.

So it is a piece of software, a server, that you run on a server.

It can be on the same server as your web server.

It can be on a different box altogether.

But it essentially is a mechanism that stores whatever you want in RAM.

And it does this in the PHP context with code like this.

So Memcache can be used by all sorts of languages.

Here is PHP's own interface to it.

And you use Memcache as follows.

You first connect to the Memcache server using Memcache connect, which

is very similar in spirit to MySQL connect, which you might recall

from a few lectures back.

Then we try, in this example, to get a user.

So the context here is, it's pretty expensive

to do select star from users on my database table.

Because I've got millions of users in this table.

And I'd really rather not execute that query more often than I have to.

I'd rather execute it once, save the results in RAM,

and the next time I need that user, go into the RAM,

go into the cache to get that user rather than touching the database.

So there's this sort of tier of performance objectives.

Disk is slow, right?

Spinning disks, especially slow.

But fast to serve up.

So generally, you might want to store something instead of on disk.

You want to store it in a table that has indexes

so that you can search it more quickly.

For instance, think back to project zero.

The XML file is relatively small.

But at the same time, any time you wanted to search it,

you had to load it from disk, build up a DOM,

thanks to the simple XML API, then search it.

Kind of annoying.

It'd be nice if we could skip the disk step

so that things would just be faster.

And thus was born MySQL in project one.

MySQL is a server, which means it's always running.

It's using some RAM.

So in that case, you have the ability to execute queries

on data that's hopefully in RAM.

But even if it isn't, you at least have the opportunity

to define indexes, primary keys, unique keys, index fields,

so that at least you can search that data more readily than you

can with, say, XPath in XML.

So the next step is not even to use a database,

because database queries can be expensive relative to just a cache,

which is just a key value store.

I want to give you x equals y.

And the next time I ask for x, you give me y.

And I want it quick, much faster than a database would return it.

So here we've gone and connected to the memory cache, daemon, the server.

In the second line, I am trying to get something from the cache.

The arguments to memcached get take the first argument

is a reference to the cache that you want to grab something from.

And then $ID just represents something like 1, 2, 3,

the ID of the user that I want to get.

If the user is null, what's the implication, apparently?

Isaac?

Well, you do the query all over again.

OK, good.

But in what case would a user be null, do you think?

When they don't exist.

Good.

When they're not in the cache.

User 1, 2, 3, or whoever I'm looking for, is not in the cache.

That variable is going to be null.

And so we do this if condition, as Isaac says.

And here, there's some somewhat familiar code,

PDO, which relates to MySQL in our case.

We connect to the database using that user in past.

We then execute the query function in PDO.

In this case, select star from users where ID equals ID.

I'm not escaping ID, because in this case,

I'm assuming that I know it's an integer.

So it's not a dangerous string, just to be clear.

Then I'm calling fetch to get back an associative array of my data,

the user's name, email address, ID, whatever else I've got in my database.

But then the last thing I do before, apparently nothing else,

because this is out of context, before actually

using that user for anything, what am I doing with him?

Axel?

You're storing it in the cache.

Exactly.

I'm storing a key value pair in the cache, whereby the key is the user's ID.

So this implies that there's an ID field in the user object that

came back from the database, from this line here,

and the value is the user object itself.

So again, a memcache, in this case, is a key value storage mechanism.

And the next time I want to look up this user,

I want to look him up by his ID.

And case in point, that's what I did in line two, up top.

Now, caches are finite, because RAM is finite, and even disk is finite.

So what could happen eventually with my cache,

just by nature of those constraints?

Axel?

It gets so big, you can't keep it on the machine.

Good.

So eventually the cache could get so big,

you can't keep it on the machine.

So what would be a reasonable thing to do at that point,

when you've run out of RAM or disk space for your cache?

You're the person implementing memcache itself now.

What do you do in that case?

You could just kind of quit, unexpected error.

But that would kind of be bad, and completely unnecessary.

What could you do?

Isaac?

Oops, sorry?

AUDIENCE MEMBER 2 garbage collection.

Yeah, so some kind of garbage collection.

And which things would you collect?

What things would you remove from memory?

AUDIENCE MEMBER 2 the user, the list.

Good.

AUDIENCE MEMBER 2 hasn't been used in a while.

So we can essentially expire objects based on when they were put in.

So if I put in user 123 yesterday, and I haven't touched him since,

or needed him since, and I need more space, well, out goes user 123.

And I can reuse that space, that memory, for user 456,

if user 456 is the next person I'm trying to insert into the cache.

So indeed, this is a very common mechanism, whereby the first one in

is the first one out, if that object has not been needed since.

By contrast, if 123 is just one of these power users who's logging in quite a

bit, and he or she is logging in again, and again, and again, well,

I should remember, every time, and we don't see it in the code here,

but every time I get a cache hit, and I actually

find user 123 in the cache, I could somehow

execute another memcache function that just touches the user object,

so to speak, thereby updating his timestamp to be this moment in time,

so that you remember that he was just selected.

And hopefully, memcache get itself would do that for us.

And indeed, it does.

I don't need to do this manually.

The cache software would remember, oh, you asked for user 123.

I should probably move him back to the front of the line,

so that the person at the end of the line

is the first one to get evicted next time around.

So it's a wonderfully useful mechanism.

And Facebook is very read-heavy or very write-heavy, if you're a user?

It's kind of both these days.

You know, early on, it was much more read-heavy than write-heavy,

because there were no, like, status updates,

and you would just have your profile, and that was about it.

So these days, there's definitely more writes,

but I'm going to guess that reads are still more common than not.

Right, when you log, if you're a Facebook user,

and you log into your account, and you see your news feed,

you might have 10, 20, whatever friends show up in that news feed.

That's potentially, like, 10 or 20 queries of some sort.

And yet, you're probably not going to update your status 30 times

in that same unit of time.

So odds are, Facebook is still a little more read-heavy, which

makes caches all the more compelling.

Because if your own profile isn't changing all that often,

at least you might get 10-page views, 100-page views by friends

or random strangers before you actually update

your status or your profile again.

That's an opportunity for optimization.

So early on, and to this day, Facebook uses things like Memcache quite a bit

so that they're not hitting their various databases just

to generate your profile.

They're instead just getting the results of some previous lookup,

unless it has since expired.

Well, onto MySQL optimization, so that you can squeeze all the more

performance out of your setup.

So this table is a little more overwhelming right now

than it needs to be.

But recall our discussion about MySQL storage engines some time ago.

And we talked briefly about MyISAM and InnoDB.

Does anyone remember at least one of the distinguishing characteristics

of those two storage engines?

And again, a storage engine was just like the underlying format

that was used to store your database data.

Good.

So InnoDB, which is the default these days,

so you haven't really needed to think about this much since Project 1.

InnoDB supports transactions, whereas MyISAM does not.

MyISAM uses locks, which are full table locks,

but does tend to have some other properties.

And this list here is a very long list of the various distinctions

among these several storage engines.

Transactions is one of them.

But there's a few other storage engines here

that I thought I would just draw our attention to.

So one, you have a memory engine, otherwise known as a heap engine.

This is a table that's intentionally only stored

in RAM, which means if you lose power, server dies or whatnot,

the entire contents of these memory tables will be lost.

But still kind of a nice feature, if you yourself

want to implement a cache relatively easily by writing keys and values

into your database, into two columns maybe,

you yourself can implement some kind of cache

to avoid having to touch maybe much larger tables that you yourself have.

So that's an option to you.

Archive storage engine.

Haven't had to use this, but take a guess as to what it does.

Besides archiving something.

What does this engine do for you, do you think?

Go ahead.

It doesn't seem to be doing very much.

It only just stores everything in the table at first and then

in the pipeline.

And what was the last sentence?

The last part of your comments?

It doesn't store anything in cache.

You even query it all the time.

Oh, it doesn't store anything in cache.

You have to query it all the time.

Not quite.

So the property you're actually getting, and you can kind of see it here,

but there's some footnotes on the other storage engines,

is it's compressed by default.

So archive tables are actually slower to query,

but they're automatically compressed for you,

so they take up much, much less space.

So a common use case for archive tables might be log files,

where you want to keep the data around and you want to write out

a whole bunch of values in a row every time someone hits your web server,

any time something buys someone.

But suppose you rarely query that data.

You're keeping it for posterity, for research purposes,

for diagnostic purposes, but you're not going

to do any selects on it any time soon.

So it would just be a waste to use more disk space than you need to.

So you're willing to sacrifice some future performance

when you do need to query it for some long-term disk savings.

So the archive format allows you to do that.

NDB is a network storage engine which is used for clustering,

so that actually there is a way of addressing

the issue of single points of failure that we discussed earlier

with shared storage, but we'll see a simpler approach in just a moment.

So, in the world of databases, like MySQL,

they typically offer this replication feature that I mentioned earlier.

So replication is all about making automatic copies of something.

And the terminology generally goes as follows.

You generally have a master database, which

is where you read data from and write data to.

But, just for good measure, that master has one or more slave databases

attached to it via a network connection.

And their purpose in life is to get a copy of every row that's

in the master database.

You can think of it rather simply as, any time a query is executed

on the master, that same query is copied down to one or more slaves

and they do the exact same thing.

So that, in theory, the master and all of these slaves

are identical to one another.

So what's the upside now of having databases one, two, three, and four,

all of which are copies of one another, apparently?

What problems does this solve for us, if any?

Axel?

Well, database one dies if somebody trips over the core piece of the green card.

Good.

So if database one dies because of human error, you trip over the core,

hard drive dies, RAM fizzles out, whatever the case may be,

you have literally three backups that are identical.

So there's no tapes involved.

There's no backup server.

I mean, these are full-fledged databases.

And in the simplest case, you could just unplug the master, plug in the slave,

and voila, you now have a new master.

And you might have to do a bit of reconfiguration in the databases

to promote him to master, so to speak, and then leave servers three and four

as the new slaves while you fix server number one.

But that would be one approach here.

So you have some redundancy, even though you

might have a little bit of downtime.

At least you can get back up and running quickly.

And indeed, you could automate this process.

If you notice that the master is down, you

take him offline completely, promote the slave,

and reconfigure them all just by writing a script.

How else could we take advantage of this topology?

Let me ask a more leading question.

In the context of Facebook, especially early days,

how might they, in particular, have made good use of this topology?

Axel?

Well, maybe if you get a lot of queries,

you can outsource them to different slaves.

OK, so if you're getting a lot of queries,

maybe you could just load balance across database servers.

And absolutely, you could.

The load balancers don't have to be used for HTTP alone.

You could use it for MySQL traffic.

But why do I say Facebook in particular?

Early on, they didn't get that many queries.

But this was still a good paradigm for them.

Yeah, why is this good, perhaps?

So back to my hypothesis that they're more read-heavy than write-heavy.

How can you adapt that reality to this particular topology, effectively?

Or put another way, why is this a good topology for a website that

is very read-heavy and less write-heavy?

Ben?

Well, if you're reading a lot of code, you can just load balance and read it.

If you have to write it, you can write it four times.

OK.

But if you're not writing it four times, you can't read it as much.

OK, good.

So reading can be expedited.

So if we combine Ben and Axel's proposals here,

for a read-heavy website like Facebook, certainly in the early days,

you could just write your code in such a way that any select statements

go to databases two, three, or four.

And any inserts, updates, or deletes have to go, apparently,

to server one, which, even though that query then

has to propagate to servers two, three, and four, it is less common.

And that happens automatically.

So the code-wise, you don't have to worry about it too much.

And if you're suffering a bit of performance there,

well, you can just throw more servers at it

and have even more read servers to lighten the load further.

So this approach of having slaves that can typically

be used either for redundancy, so you just have a hot spare ready to go,

or so that you can balance read requests across them

is a very nice solution.

But of course, every time we solve one problem, we've introduced another.

Or at least we haven't fixed yet another here.

What is a fault in this layout still?

Be paranoid.

Kind of talked about it earlier, but what if one dies?

There's got to be some blip on the radar here,

because we have to promote a slave.

So you still have a single point of failure here, at least for rights.

We could keep Facebook alive by letting people browse profiles and read

profiles, but status updates, for instance, could be offline.

For as long as it takes us to promote a slave to a master.

Feels like it'd be nicer, or at least our probability

would be better of uptime, if we instead had not just a single master,

but again, let's just throw hardware at the problem.

So another common paradigm is actually to have a master-master setup,

whereby, as the labels imply and as the arrows suggest,

this time you could write to either server 1 or 2.

And if you happen to write to server 1, that query

gets replicated on server 2, and vice versa.

So now you could keep it simple.

You could always write to 1, but then the query

goes to number 2 automatically.

Or you could write to either, thereby load balancing across the two,

and they'll propagate between each other.

But in this case here, if you've laid out your network connections

properly, either 1 or 2 can go down, and you still

have a master that you could read from.

And you could even implement this in code.

Very simply, we had the MySQL connect function weeks ago,

or even the PDO constructor function, which tries to connect to a database.

You could implement this in PHP code.

If MySQL connect fails when connecting to server 1, then just try server 2.

So you yourself could build in some redundancy

so that now we could lose server 1 or 2,

and not have to intervene as humans just yet,

because we at least still have a second master

that we can continue writing to, even though server 1 is now

offline for some amount of time.

All right, but we still have to route traffic there.

So in pursuit of this idea of load balancing,

here's a more complex picture that starts

to unite some of our web ideas and some of our database ideas.

So at the top there, we have some kind of network.

We have a load balancer in between.

And then we have this front end tier.

So web servers are typically called a tier, a service tier.

This is a multi-tiered architecture, would be the jargon here.

And those web servers now apparently are routing their requests through what

in order to reach some MySQL slaves for reads?

Who's the man in the middle here?

Yeah, Axel?

AUDIENCE MEMBER 4 For reads, it would be the load balancer.

OK, so for reads, yeah.

We have a second load balancer depicted here.

Frankly, in reality, they could be one and the same.

They could be the same device, but just listening

for different types of connections.

But for now, they're drawn more simply as separate.

Now we have one MySQL master, so we also have wires or arrows pointing

from the web servers to the master.

And the master, meanwhile, has some kind of connection to the slaves.

So not bad.

No, frankly, this is starting to hurt my brain,

because now what was a very simple class where

you have a nice self-contained appliance on your laptop,

does everything, web, database, caching, anything you want it to do?

My god, look at all the things we have to wire up now.

And it's still not perfect.

What could die here?

What are our single points of failure?

Jack?

Oh, Isaac?

Sure.

Okay, so the MySQL master. We haven't really solved that problem, so

kind of be nice to steal part of the previous picture and maybe

insert it into here. Jack?

Same thing. Axel?

Load balancers, right? So single point of failure is

very well defined. Like single point of failure, just look for any

any bottlenecks here whereby things point in and then go out.

Load balancer is one here, load balancer is one there.

So it turns out with load balancers, for your $100,000,

you can get two of them, typically, in the package.

And what they tend to do is operate also in what's called,

similar in spirit to master-master mode, but in the context of load

balancers, it's typically called active-active as opposed to

active-passive.

And the idea here is with active-active, you have a pair

of load balancers that are constantly listening for

connections, either one of which can receive packets from the

outside world and then relay them to back-end servers.

And what they typically do is they send heartbeats from left

to right and right to left, so that if this guy ever stops

hearing a heartbeat from this guy, so to speak, and a heartbeat

is just like a packet that gets sent every second or

something like that.

If this guy stops hearing a heartbeat from this guy, he

automatically assumes that this guy must have gone offline, so

he's completely in charge now, and he continues to send traffic

from the outside world in.

Or if you instead have active-passive mode, if this is

the active guy at the moment, or rather, if this is

the active guy at the moment and he dies, this guy

similarly detects, ooh, no more heartbeat.

And what the passive guy will do is promote himself

to active, which essentially just means he takes over the other

guy's IP address, so that all traffic now comes to him.

So in short, we definitely need another load balancer in the picture.

How it's implemented is not as important to us right now,

but having a single load balancer is probably a bad thing, right?

And this is the tragedy.

You can throw money at, you can throw a lot of brain power

at various tiers here, but if you have a lot of web

servers, a lot of MySQL servers, but you have one load balancer

just because it was really expensive or you didn't know how to configure

it properly, the rest of it is pretty much for naught,

because you still have things that can die and take down

your entire website.

So let's make this more complex still.

So let's now introduce two load balancers, and let's actually

introduce an idea of partitioning.

And this was actually something that Facebook, coincidentally,

did make good use of early on.

Back in the day, there was harvard.thefacebook.com.

There was mit.thefacebook.com.

And the earliest partitioning that they used was to essentially

have a different server, as best outsiders could tell, for each school.

So they literally just copied the database,

copied the files over to another server, and then voila,

thus was born MIT's copy of Facebook.

But this is actually, even though this would get kind of messy

for 800 million users and thousands and thousands of universities

and networks, it's pretty clean early on,

because it just leverages this idea of partitioning.

Facebook didn't have a big enough server to handle Harvard and MIT,

so why not just get two and say Harvard users go here,

MIT users go here, and now we've kind of avoided that problem.

Now, unfortunately, when BU comes on, we need a third server,

but at least we can scale horizontally.

Now, there is a catch with partitioning.

As soon as you wanted to be able to poke someone at MIT or vice versa,

you had to somehow cross that Harvard-MIT boundary, at which point

it's kind of a bad thing that they're all in separate databases.

So early on, there were some features that you could only

do within your own network, not until there was more shared state,

could you send messages and the like.

So partitioning, though, could be used even more simply.

Suppose that you just had a whole bunch of users.

Well, you need to scale your architecture horizontally.

Why don't I just put users whose last name start with A to M

on half of my servers, and then N through Z on the others?

And when they log in, I just send them to one or the other server

based on that.

So in general, partitioning is not such a bad idea.

It's very common in databases, because you can still have redundancy.

Whole bunch of slaves in this case here, whole bunch of slaves over here.

But you can balance load based on some high-level user information,

not based on load, not round robin.

You can actually take into account what someone's name is,

and then send them to this particular server.

So partitioning is a very common paradigm.

And then lastly, just to slap a word on it,

high availability refers to what we described

in the context of load balancers, but it can apply to databases as well,

whereby high availability, or HA is the buzzword,

simply refers to some kind of relationship

between a pair or more of servers that are somehow

checking each other's heartbeats, so that if one of them dies,

the other takes on the entire burden of the service that's

being provided, whether a database or whether a load balancer.

So even though we finally got the iPad working,

it's a little small to draw on.

So what I wanted to do, as our final example here,

is let me raise the screen here.

One of these buttons will do it.

All right, we're going old school now.

Our first and last piece of chalk in the class.

Let's see.

Let's see.

Start with the middle one.

All right, let's build ourselves a network here.

So we have a need for one or more web servers, one or more databases,

maybe some load balancers, but we're also

going to try to tie together last week's conversation about security,

so we'll have to think about firewalling things out now.

So in very simple form, we have here a web server, which I'll draw as www.

All right, so that's our web server.

And now my website's doing so well that I need a second web server,

so I'm going to draw it like this.

And now we need to revisit the issue of balancing load.

So what felt like one of our best options here?

How do I still have the internet, which I'll draw as a cloud here,

connected to both of these servers somehow,

but I want the property of sticky sessions?

So what are my options, or what was my best option?

How do I implement sticky sessions?

Axel?

AUDIENCE MEMBER 2 Use a load balancer and keep all the sessions in one place.

OK, good.

So use a load balancer and store all the sessions in one place.

And that's not OK.

So we can actually do one, but not necessarily both of those.

Let me interpose now the thing we started calling a black box.

So this is some kind of load balancer.

Now I still have my back end servers.

And here's another one here.

OK, and now this is connected here, but I still want sticky sessions.

But you know what?

Shared states, that sounded expensive.

Fiber channel, iSCSI, it sounded complicated.

There's a simpler way.

How do I ensure that I get sticky sessions using only a load balancer

and no shared state yet?

How can I ensure that when Alice comes in and she's

sent to this server the first time, that the next time she comes in,

she's sent to the same one?

Axel?

AUDIENCE MEMBER 3 Remember which server she visits, either for a cookie

or saving it in your load balancer.

OK, good.

So why don't we have the load balancer listen at the HTTP level.

And when the response comes back from the first web server,

let's give them numbers.

So let's call this 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,

let's call this 1 and this guy 2.

The load balancer can insert some kind of cookie

that allows it to remember that this user belongs on server 1.

And how it does that, I don't know.

It's a big random number, and it's got a table like PHP does for its sessions

and figures out which server to send her to in this case.

All right, so now I have a database.

The easiest way I know how to set up a database

is to put it on the web server itself.

So much like the CS50 appliance, you have a database in the same box

as a web server.

If I now have a database here and here on the same boxes as our web servers,

what's the most obvious problem that now arises?

Yeah?

AUDIENCE 2 Well, Alice's shopping cart is, oh, well,

if she does something to her profile or whatever,

it's just going to be on server 1 and not on server 2

since she just visited server 1.

DAVID MALAN.

So if Alice just happens to end up on server 1

and she updates her profile or credit card information

and she does something persistent, not the shopping cart thing because that

involves the session, but she does something persistent,

it's going to persist on this database, and that's

fine because sticky sessions are solving all my problems now.

But she comes back in a week or she logs in from a different computer,

cookie expires, whatever, and she ends up here.

What happened to my credit card information?

What happened to my profile?

I now have no profile because I'm on a different database.

So clearly, this is not going to fly unless we partition our users

and have the load balancer actually take into account who is this user

and then send the user based on Alice's last name always to the same server.

So that could be one approach.

But for now, let's instead factor out the database

and say that it's not on the web servers, it's separate,

and it's got some kind of internet connection here.

Of course, we've solved one problem, but introduced a new one,

which is what?

Isaac?

Isaac?

AUDIENCE MEMBER 1 Single point of failure.

DAVID J. MALAN So single point of failure again.

So how can we mitigate this?

Well, we can do a couple of things.

We can attach slave databases off of this, and that's kind of nice.

But it then involves somehow promoting a slave to a master in the event one

dies, so maybe the cleanest approach would be something

like two master databases.

So we'll call this DB1.

This will be DB2.

And now, how do I want to do this?

Connect these like this?

Isaac, you shook your head.

AUDIENCE MEMBER 2 Well, you could connect the two databases to each other.

DAVID J. MALAN OK.

So we should probably do this for master-master replication,

so that's good.

But what about these lines?

Good?

Bad?

Answer's bad.

Why bad?

Jack?

AUDIENCE MEMBER 2 Well, you can connect each one to both of the databases.

DAVID J. MALAN Right.

So the problem we just identified was database on same server

is web server bad, because then it's talking only to it.

And if Alice ends up on the other server, she has no data

that you're expecting.

Well, functionally, this is equivalent.

I've just drawn a line, but they're still only connected to each other.

And the traffic should probably not go like that.

So we at least need to have some kind of cross-connect.

So OK, so I can do this.

But now what do I do?

So now my load balancing has to be done in code.

If those are the only components in my system right now,

the line suggests that www1 has a network connection to db1 and db2.

But that means now I have to do something like an if condition

only in my PHP code to say, if this database is up, right here,

else if this database is up, right there.

And that's not bad, but now your developers

have to know something about the topology.

If you ever introduce a third master or something like that,

although MySQL wouldn't play nicely with that,

now you have to change your code.

This is not a nice layer of abstraction.

So how else could we solve this, Axel?

I don't like the idea of connecting each of my web servers to the database.

Because frankly, you know what?

This is going to get really ugly if it starts looking like this.

Very quickly, this degrades into a mess.

Yeah?

Get another machine, load balancer, if you will.

OK, good.

It handles all of that.

So connect your www servers to the load balancer,

and then let it handle requests.

And then you can implement all kinds of features.

Like say, they are both masters, right?

They have the same data.

What if only users with a last name that starts with m logs in?

Well, you're going to have a load on one particular server.

But then the load balancer can take all those features

we talked about, CPU cycles and all that,

and actually distribute MySQL queries across databases.

OK, good.

So we insert a load balancer here, which is connected to both the www machines

and also the database servers.

And then he can be responsible for load balancing across the two masters.

It's actually harder for the database to do any kind of intelligence load

balancing based on last names at this point,

since the MySQL traffic is going to operate with binary messages,

not with HTTP style textual messages.

Load balancer up here can look at HTTP headers

and make intelligent decisions.

It's harder, and maybe not impossible, but it

wouldn't be very common to do load balancing based on application layer

intelligence here.

You would probably push that to the PHP code again in that case.

But this isn't bad.

But Isaac doesn't like this picture now because of what?

AUDIENCE MEMBER 2 It still fails at one point.

DAVID J. MALANYIKA Yeah, so we still have this single point of failure.

This would have cost me even more money or more complexity.

Even if I'm using free software, this just takes more time now.

So now we have load balancer one, load balancer two.

I need to do something like this.

And even though this looks a little ridiculous,

oh, actually it's a little elegant.

That's pretty sexy.

So you would do this with switches or some kind of ethernet cables

all going to some central source.

So suppose instead we actually did that.

If you've ever plugged in a computer into a network jack, which most of you

probably have, even if you have a laptop,

you don't connect these computers all to themselves.

You instead connect them to a big switch that has lots of ethernet ports

that you can plug into.

But now, Isaac, what do you not like about this idea

if I'm plugging everything into a switch?

AUDIENCE MEMBER 3 It still fails.

DAVID J. MALANYIKA Yeah, so welcome to the world of network redundancy.

So really the right way to do this is to have two switches.

So almost every one of your servers, database and web

as well as your load balancers would typically

have at least two ethernet jacks in them.

And one cable would go to one switch.

Another cable would go to the other switch.

You have to be super careful not to create loops of some sort.

So switches have to be somewhat intelligent, typically,

so that you don't create this crazy mess where traffic is just bouncing

and bouncing around in your own internal network and nothing's getting in or out.

So there's some care that has to be taken.

But in general, this is really the theme,

in ensuring that you have not only scalability, but redundancy

and higher probabilities of uptime and resilience against failure.

You really do start cross-connecting many different things.

But let's push harder.

Isaac, suppose I fix the switch issue.

Suppose I also make this two load balancers and fix that issue.

What's something else that could fail now?

I can't do this on an iPad very well.

So this is your data center.

Here's the door to your data center.

Jack?

The building burns down.

That's good.

More extreme than I had in mind.

I was thinking the power goes out.

But that works, too.

So the building itself burns down or goes offline.

You have some kind of network disconnect between you and your ISP,

the whole building.

Or the power indeed does go out.

And this has happened.

In fact, one of the things that happens every time Amazon goes out

is the whole world starts to think that cloud computing, so to speak,

is a bad thing because, oh my god, look, you can't keep the cloud up.

But the tragedy here is in this perception

that cloud computing really just refers to outsourcing of services

and sharing resources like power and networking and security

and so forth across multiple customers.

So Amazon services, EC2, Elastic Compute Cloud,

is kind of this picture here whereby you don't own the servers,

but you do rent space on them because they give you

VPSs that happen to be housed inside of this building.

Amazon offers things called availability zones

whereby this might be an availability zone called US East 1.

So this is a building in Virginia in that particular case.

And what they offer, though, is US East 2 and 3 and 4,

but they call them A and B and C and D.

And what that simply means, in theory, is

that there's another building like this drawn over there that does not

share the same power source, does not share the same networking cables.

And so even if something goes wrong in one building, in theory,

the other shouldn't be affected.

However, Amazon has suffered outages in multiple availability zones,

multiple data centers.

So in addition to having servers in Virginia,

guess where else they have servers?

OK.

Anywhere else.

That's actually a pretty hard question.

The world's a big place.

So the West Coast.

And in Asia and in South America and in Europe as well,

they have different regions, as they call them,

inside of which are different data centers or availability zones.

But this just means that you can really drive yourself crazy thinking

through all the possible failure scenarios

because even though Jack's building burning down is a little extreme,

things like that do happen.

If you have a massive storm, like a tornado or a hurricane,

that just knocks out power, absolutely could a whole building go down.

So what do you do in that case?

Well, we have to have a second data center or availability zone.

I'll draw it much smaller this time, even though it

might be physically the same.

So here's another one.

Suppose that inside of this building is exactly that same topology.

So now really what we have is the internet outside these boxes

connecting to both buildings.

So internet is no longer inside the building.

So once you have two data centers, how do you now distribute your load

across two data centers?

Axel?

Well, then you can use the DNS trace we used.

Yeah, so we didn't really spend much time on it,

but recall that you can do load balancing at the DNS level.

And this is indeed how you can do geography-based load balancing,

whereby now when someone on the internet requests

the IP address of something.com, they might get the IP address,

really, of this building, or more specifically,

of the load balancer in this building.

Or they might get the IP address of the load balancer in this building.

When we did the NS lookup on Google, we got a whole bunch of results.

That's not because they have one building with lots

of load balancers inside of it.

That's because they probably have lots of separate buildings or data

centers, different countries even, that themselves

have different entry points, different IP addresses.

So you have global load balancing, as it's typically called.

Then the request comes into a building.

And you still have the issue of somehow making sure

that subsequent traffic gets to the same place,

because odds are Google is not sharing your session across entirely

different continents, even though they could be.

But that would probably be expensive or slow to do.

So odds are you're going to stay in that building for some amount of time.

But again, these ideas we've been talking about just

get magnified the bigger and bigger you start to think.

And even then, you have potential downtime,

because if a whole building goes offline,

and your browser or your computer happens

to have cached the IP address of that building, that data center,

could take some minutes or some hours for your TTL

to expire, at which point you get rerouted to something else.

Not too long ago, just a few weeks, I think Quora

was offline for several hours one night, because they use Amazon.

A bunch of other popular websites, too, who use Amazon services

were down altogether, because they were in a building or a set of buildings

that suffered this kind of downtime.

And it's hard.

If you are having the fortunate problem of way too many users

and lots of revenue, it gets harder and harder

to actually scale things out globally.

So typically, people do what they can.

But as Isaac has gotten very good at pointing out,

you can at least avoid, as best as possible,

these kinds of single points of failure.

Questions?

So a word on security, then.

Let's focus only on this picture, not so much on the building.

What kind of traffic now needs to be allowed in and out of the building?

So let me go ahead and just give myself some internet here,

connecting to the load balancer somehow.

What type of internet traffic should be coming from the outside world

in if I'm hosting a website, a LAMP-based website?

Yeah.

Well, you would want a firewall that allows only for 80 connections.

OK, good.

So I want TCP, recall, which is one of the transport protocols,

80 on the way in.

That's good, but you just compromised my ability to have certain security.

Why?

You're now blocking a very useful type of traffic.

Good.

So we also want 443, which is the default port that's

used for SSL, for HTTPS-based URLs.

So that's good.

This means now that the only traffic allowed into my data center

is TCP 80 and 443.

Now, those familiar with SSH, you've also just

locked yourself out of your data center because you cannot now

SSH into your data center.

So you might want to allow something like port 22 for SSH,

or you might want to have an SSL-based VPN so that you can connect somehow

to your data center remotely.

And again, it doesn't have to be a data center.

This can just be some web hosting or some VPS hosting company

that you're using.

And OK, so we might need one or more other ports for our VPN,

but for now that's pretty good.

How about the load balancers?

What kind of traffic needs to go from the load balancer to my web servers?

Axel?

Well, it's really a mess to keep it encrypted

because once it's inside the data center,

nobody else is going to listen than the people inside the data center.

So you would want to drop the encryption and do 80.

Good.

And that's actually very common to offload your SSL to the load balancer

or some special device and then keep everything else unencrypted.

Because if you control this, it's at least safer.

Not 100%, because if someone compromises this,

now they're going to see your traffic unencrypted.

But if you're OK with that, doing the SSL termination here,

so everything's encrypted from the internet down to here,

but then everything else goes over normal, unencrypted HTTP.

The upside of that is, remember the whole certificate thing?

You don't need to put your SSL certificate on all of your web

servers.

You can just put it in the load balancer or the load balancers.

You can get expensive load balancers to handle the cryptography

and the computational costs thereof.

And you can get cheaper web servers because they

don't need to worry as much about that kind of overhead.

So that's one option.

So CCP80, here and here.

How about the traffic between the web server and the databases?

Perhaps through these load balancers.

This is more of a trivia question.

But what kind of traffic is it, even if you don't know the port number?

Yeah?

AUDIENCE MEMBER 2 It's query or execute.

DAVID J. MALANYIKA Yeah, query, execute, or more specifically,

it's the SQL queries, like select and insert and delete and so forth.

So this is generally TCP 3306, which is the port number

that MySQL uses by default.

So what does this mean?

If you do have firewalling capabilities, and we haven't

drawn any firewalls, per se, so we do need to insert some hardware

into this picture that would allow us to actually make

these kinds of configuration changes.

But if we assume we have that ability, in large part

because all of these things are plugged in, as we said,

to some kind of switch, we assume that we

plug in, as we said, to some kind of switch.

Well, the switch could be a firewall itself,

and we could make these configuration changes.

We can further lock things down.

Why?

I mean, everything just works if I don't firewall things.

Why would I want to bother tightening things

so that only 80 and 443 are allowed here, and 3306 is allowed here?

And in fact, notice, there's no line between these guys.

Well, it would be really stupid to keep, for example, 3306 open

in the first firewall, because then people, they might not

be able to, because of other security metrics.

But in theory, they are allowed by the firewall to query your database

and do SQL commands.

Good.

Exactly.

There's just no need for people to be able to potentially even execute

SQL queries coming in or make MySQL connections.

And even if you're not even listening for MySQL connections,

it, again, is sort of the principle of the thing.

You should really have the principle of least privilege,

whereby you only open those doors that people actually have to go through.

Otherwise, you're just inviting unexpected behavior,

because you left a door ajar, so to speak.

You left a port open, and it's not clear

whether someone might, in fact, take advantage of that.

Case in point, if somehow you screw up, or Apache screws up,

or PHP screws up, and this server is compromised, it'd be kind of nice

if the only thing this server can do is talk via MySQL to this server

and cannot, for instance, suddenly SSH to this server, or poke around,

or execute any commands on your network other than MySQL.

So at least if the bad guy takes this machine over,

he really can't leave this rectangle here that I've drawn.

So again, beyond the scope of things we've done in the class,

and even though the appliance itself actually

does have a firewall that allows certain ports in and out,

all of the ones you need, we haven't had to fine tune it for any

of the projects, realize that you can do that even on something

like a Linux-based operating system.

So in short, as soon as you have the happy problem

of having way too many users for your own good, lots of new problems

arise, even though thus far we've focused pretty much entirely

on the software side of things.

So that is it for Computer Science S75.

I'll stick around for questions one on one.

We still have a final section tonight for those of you

who would like to dive into some related topics.

Otherwise, realize that the final Project 2, its deadline is coming up.

You should have gotten feedback from your TFs about Project 1.

If not, just drop him or her a note, or me.

Otherwise, it's been a pleasure having you in the class.

We will see you online after tonight.

Oh, that's OK.

Thanks.

I wasn't trying to build up to that there.
