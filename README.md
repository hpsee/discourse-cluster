# Discouse Cluster

This is a small example of using Python to extract posts from a discourse board,
and then using the data to do a simple clustering. You can [view the plots](https://hpsee.github.io/discourse-cluster/)
to see d3 final output, or browse the notebooks to look at specific analyses:

 - [cluster-analysis-gensim-tsne.ipynb](cluster-analysis-gensim-tsne.ipynb) was the first unsupervised effort to find some natural clustering in the data. We only see that posts vary along a single dimension, and it's not clear what that is. What do you think?
 - [cluster-analysis-gensim-tags.ipynb](cluster-analysis-gensim-tags.ipynb) was a simple effort to cluster posts based on their tags. How are we doing in terms of doing the tagging? Do the groups make sense?

## Setup

### Environment

Whether you are running locally or via a container, you need 
to export your `DISCOURSE_API_TOKEN` and `DISCOURSE_API_USER`
to the environment. The token is expected to be for an admin (with a rate
limit of 60/min) so if you are a user with a lower ratelimit, you'll
need to also export a key (to be anything) for `DISCOURSE_USER_FLAG`.

```bash
export DISCOURSE_API_TOKEN=xxxx
export DISCOURSE_API_USER=myusername
```

You can optionally define these values, they will default to https://ask.cyberinfrastructure.org
for the base and q-a for the category.

```bash
export DISCOURSE_BASE=https://ask.cyberinfrastructure.org
export DISCOURSE_CATEGORY=q-a
```

You can also edit the defaults directly in the script [export_posts.py](export_posts.py)
or one off exports in [run.sh](run.sh).

### Data Folder

We'll also want to create a folder to save data to:

```bash
$ mkdir -p data
```

## Local Usage

### 1. Batch Export

After exporting environment variables, you should first look at, and then
can use the [run.sh](run.sh) script. to generate one or more exports for
different cateories. For example, the default script exports q-a for 
[Ask Cyberinfrastructure](https://ask.cyberinfrastructure.org/) and then the discussion zone category, and assumes an admin token with up to 60 requests per minute.

The files will be export under data, in a folder named by the date,
and files named according to the api base, the category, and the content.

### 2. Export Posts

You can also run the Python script manually. Just run the script, and direct data to be output in data/.

```bash
$ ./export_posts.py data
Getting https://ask.cyberinfrastructure.org/c/q-a.json
Getting https://ask.cyberinfrastructure.org/c/q-a.json?page=1
Getting https://ask.cyberinfrastructure.org/c/q-a.json?page=2
Getting https://ask.cyberinfrastructure.org/c/q-a.json?page=3
Getting https://ask.cyberinfrastructure.org/c/q-a.json?page=4
Found 138 topics, and 150 top tags!
```

The first part shown above exports the entire list of topics (without text details),
and for this data output folder will have a set of data files (json), each named with the board,
cateogory, and date of export. 

```bash
$ tree data/2019-10-19/
├── ask.cyberinfrastructure.org-q-a-tags-2019-10-19.json
└── ask.cyberinfrastructure.org-q-a-topics-2019-10-19.json
```

The second half of the script exports a json structure for each post,
and a single posts json structure that has all raw text content. You can
use the individual post files to get metadata, and use the posts entire
export for the content (it's a dictionary indexed by the post id).
For example, here are a few posts (note they each have an id) and
the export of text content (the last one):

```
├── ask.cyberinfrastructure.org-q-a-post-943-2019-10-19.json
├── ask.cyberinfrastructure.org-q-a-post-98-2019-10-19.json
└── ask.cyberinfrastructure.org-q-a-posts-2019-10-19.json
```

**Important** There are different API request limits based on your role
on the board. If you are an admin, you get 60/min. If you are a user, you
get up to 20/minute, up to a daily maximum of 2880. See [this page](https://meta.discourse.org/t/global-rate-limits-and-throttling-in-discourse/78612) for more details.


The topics should be all that you need, as each one includes it's
own tags. The "tags" export is the "top_tags" as determined by the 
discourse API, and probably is redundant.

### 3. Cluster Posts

We are going to try using [Doc2Vec](https://radimrehurek.com/gensim/models/doc2vec.html) on the sentences for each post, and then generating embeddings, and using kmeans for the embeddings. Since I didn't want to install a ton of Python libraries on my host, I decided to build a container to generate the notebook.

```bash
$ docker build -t vanessa/askci-cluster-gensim .
```

You actually don't need to do this if you don't want to, the container
is provide on [Docker Hub](https://hub.docker.com/r/vanessa/askci-cluster-gensim/tags) (note
that I've also tagged a version for the date of data export). Either way, 
then run the container, and map port 8888 to expose the notebook.

```bash
$ docker run -it -p 8888:8888 vanessa/askci-cluster-gensim
```

*sidenote* I really dislike notebooks for reproducible work generally, but
decided to use one here to make it easy to show the work on GitHub and
generate plots inline. 

If you run the container and make changes that you want to keep, 
what you'll need to do is interact with the notebook
in your browser (given the URL that you are provided) and then Download
to your computer to save. If we bind directories there could be a whole
mess of weird permissions, but if you want to try that, it would work too.

I'm not a fan of click to download and then (still) needing to move and rename
the file, so what I wound up doing is copying the notebook and data files that I needed out
of the container, after saving. For a container named "amazing_ganguly", you
can copy both notebooks and data generated (if you run them):

```bash
# Notebooks
$ docker cp amazing_ganguly:/home/jovyan/cluster-analysis-gensim-tsne.ipynb cluster-analysis-gensim-tsne.ipynb 
$ docker cp amazing_ganguly:/home/jovyan/cluster-analysis-tags.ipynb cluster-analysis-tags.ipynb 

# Data Output
$ docker cp amazing_ganguly:/home/jovyan/askci-post-tsne-179x2.json docs/askci-post-tsne-179x2.json
for num in {1..10}; do
    docker cp amazing_ganguly:/home/jovyan/askci-tags-ica-embeddings-ncomps-${num}.json docs/askci-tags-ica-embeddings-ncomps-${num}.json
done
```
