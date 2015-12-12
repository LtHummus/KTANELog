import sched, time

s = sched.scheduler(time.time, time.sleep)


def foo(t):
    print "Hello world"
    t.enter(1, 1, foo, (t,))

print "init"
s.enter(10, 1, foo, (s,))
s.run()
