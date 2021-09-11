pre_build:
	pip install --upgrade pip && \
	pip install -r requirements.txt

deploy:
	@$(MAKE) deploy.consumer && \
	$(MAKE) deploy.producer

delete:
	@echo deleting entire stack...

deploy.consumer:
	@echo deploying consumer...
	@$(MAKE) -C xray-consumer build deploy

deploy.producer:
	@echo deploying producer...
	@$(MAKE) -C xray-producer build deploy

clean:
	find . -type d -name .aws-sam | xargs rm -rf