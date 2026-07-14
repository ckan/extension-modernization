---
icon: lucide/rocket
---

# Get started

Whether you are creating a new CKAN extension, or you are maintaining existing
one, you're likely want it to follow certain pattern so that external
contributors can easily participate in development.

Additionally, you'd like to use the latest available tools from CKAN to reduce
friction during upgrade. Instead of realizing that extension will be broken
with the next CKAN release and you must do something right now, it always
better to rely on tools that in worst case will get deprecated after the
release, so that you still can afford some level of procrastination and update
the extension when it's convenient for you.

This guide contains collection of quite opionated recommendations for different
aspcects of extension development in CKAN. Some of them may even look
overcomplicated, but if you choose to follow them, in the end you'll have the
complete checklist that can be used for CKAN upgrade. And instead of
smoke-testing the extension praying that no hidden bugs are left after the
upgrade, you'll have a clear list code units that require modification for
every CKAN version upgrade.




/// admonition | @smotornyuk: Ambiguous solutions
    type: quote

When you see such block, you are going to read over-opinionated position of the
individual mentioned in the heading. Most likely, there are different opinions
regarding the problem in question and different people tend to approach the
problem differently.

As it often happens, there is no silver bullet, and you have to consider pros
and cons of different approaches yourself. Such blocks focus your attention on
the fact that you need to decide, whether suggested way works for you. And it's
completely normal to choose your own way of solving the problem, if the
suggested approach does not fit well into your workflow.

///
