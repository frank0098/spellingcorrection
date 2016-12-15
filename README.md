# Flexible Spelling Correction


Flexible Spelling Correction framework tool that provide customized services for query and sentence correction for potential users, with the implentation of a novel query spelling correction algorithm - generaliezed hidden Markov model which is published in SIGIR’12 by Yanen Li, Duanhui Zhong and Chengxiang Zhai.( “A Generalized Hidden Markov Model with Discriminative Training for Query Spelling Correction” publication )

#Requirement: 
This software has been tested on MacOS Sierra with Python 2.7 with necessary packages installed.

#
#Usage
To use the software, first unpack the archive. The software already provides a limited dataset with trained parameters from the dataset. Users can choose to use the the dataset we provide or they can use their own dataset to meet their specific requirements. Their dataset should follow the format of the provided dataset. They also have the option to specify the path to their customized dataset by changing the paths in the conf.cfg file.

The software provides three different usages: 

1. Testing a given query in command line.
----
 In your shell types and runs:

>	python main.py test 10

Then types in your query input. The software will return the top 10 corrected queries with scores.

2. Setting up a simple Http server. 
----
In your shell types and runs:
>	python main.py server 9999

This will starts an Http server on your localhost port=9999 and serves as an spelling correction online service. This server expects a JSON object from a POST method:
```
{
	“Query”: “your query”
	“K”: 10
}
```
The server will return a JSON object with format of:
```
{
	“Corrected_query”:”[list of corrected query]”
}
```
For example, in your command line type in following line when your server is running:

>	curl --data "{\"query\":\"make america grat agan\", \"K\":\"5\"}" --header "Content-Type: application/json" localhost:9999

The expected return JSON object  will look like:
```
{
	"corrected_query": 
	["make america great adam", "make america what again", "make america great again", "make america iraq again", "make america grant again"]
}
```
3. Training parameters: 
----
In your shell types and runs:
>	python main.py train

This will runs a training process for the parameters λ and µ. It expects a user provided training set and writes the parameters to the output file.

Notice that the dataset is only for demo purpose with limited size and does not provide very accurate result.

## Directory structure
<pre>
spellingcorrection/
├── dataset
│   ├── addition.txt
│   ├── deletion.txt
│   ├── substitution.txt
│   ├── lexicon.txt
│   ├── singlecollection.txt
│   ├── unigramprob.txt
│   ├── bigramprob.txt
│   ├── doublecollection.txt
│   ├── training_params.txt
│   ├── training.txt
│   └── trainoutput.txt
├── README
├── conf.cfg  
├── main.py
├── lexicon.py
├── phrase.py
├── prob.py
├── query_correction.py
├── score.py
</pre>
