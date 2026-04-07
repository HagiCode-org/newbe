import React from 'react';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';
import { homepageContent, LearningPathStep as LearningPathStepType } from './config';

interface LearningPathStepProps {
  step: LearningPathStepType;
  showArrow: boolean;
}

function LearningPathStep({ step, showArrow }: LearningPathStepProps): JSX.Element {
  const content = (
    <div className={styles.learningPathStep}>
      <div className={styles.learningPathStepNumber}>{step.step}</div>
      <div className={styles.learningPathStepContent}>
        <div className={styles.learningPathStepTitle}>{step.title}</div>
        <div className={styles.learningPathStepDescription}>{step.description}</div>
      </div>
      {showArrow && <span className={styles.learningPathArrow} aria-hidden="true">→</span>}
    </div>
  );

  if (step.link) {
    return (
      <Link
        to={step.link}
        className={styles.learningPathStep}
        aria-label={`学习路径第${step.step}步: ${step.title} - ${step.description}`}
      >
        <div className={styles.learningPathStepNumber}>{step.step}</div>
        <div className={styles.learningPathStepContent}>
          <div className={styles.learningPathStepTitle}>{step.title}</div>
          <div className={styles.learningPathStepDescription}>{step.description}</div>
        </div>
        {showArrow && <span className={styles.learningPathArrow} aria-hidden="true">→</span>}
      </Link>
    );
  }
  return content;
}

export default function LearningPath(): JSX.Element {
  const steps = homepageContent.learningPath;

  return (
    <section className={styles.learningPathSection} aria-label="学习路径">
      <h2 className={styles.learningPathTitle}>学习路径</h2>
      <div className={styles.learningPathContainer}>
        {steps.map((step, index) => (
          <LearningPathStep
            key={step.step}
            step={step}
            showArrow={index < steps.length - 1}
          />
        ))}
      </div>
    </section>
  );
}
